"""Bonus management API router."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_admin, require_ownership_or_admin
from backend.models.bonus import Bonus, BonusStatus
from backend.models.user import User
from backend.schemas.bonus import BonusCreate, BonusReview, BonusOut

router = APIRouter(prefix="/bonuses", tags=["bonuses"])


@router.post("/", response_model=BonusOut, status_code=status.HTTP_201_CREATED)
async def request_bonus(
    payload: BonusCreate,
    token_data: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    bonus = Bonus(  # type: ignore[call-arg]
        **payload.model_dump(),
        requested_by=token_data.id,
        status=BonusStatus.pending,
    )
    db.add(bonus)
    await db.commit()
    await db.refresh(bonus)
    return BonusOut.model_validate(bonus)


@router.patch("/{bonus_id}/review", response_model=BonusOut)
async def review_bonus(
    bonus_id: int,
    payload: BonusReview,
    token_data: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    bonus = await db.get(Bonus, bonus_id)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found.")
    if bonus.status != BonusStatus.pending:
        raise HTTPException(status_code=409, detail="Bonus already reviewed.")

    bonus.status = payload.status
    bonus.approved_by = token_data.id
    bonus.approved_at = datetime.now(tz=timezone.utc)
    bonus.rejection_note = payload.rejection_note

    # Trigger Notification
    from backend.models.notification import Notification
    from backend.models.employee import Employee
    emp = await db.get(Employee, bonus.employee_id)
    if emp:
        status_text = "approved" if bonus.status == BonusStatus.approved else "rejected"
        db.add(Notification(  # type: ignore[call-arg]
            user_id=emp.user_id,
            title=f"Bonus Request {status_text.capitalize()}",
            message=f"Your bonus request for {bonus.amount} has been {status_text}. {bonus.rejection_note or ''}",
            category="bonus",
        ))

    await db.commit()
    await db.refresh(bonus)
    return BonusOut.model_validate(bonus)


@router.get("/employee/{employee_id}", response_model=list[BonusOut])
async def get_employee_bonuses(
    employee_id: int,
    status_filter: BonusStatus | None = Query(default=None, alias="status"),
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Bonus).where(Bonus.employee_id == employee_id)
    if status_filter:
        q = q.where(Bonus.status == status_filter)
    q = q.order_by(Bonus.created_at.desc())
    bonuses = (await db.execute(q)).scalars().all()
    return [BonusOut.model_validate(b) for b in bonuses]


@router.get("/pending", response_model=list[BonusOut])
async def get_pending_bonuses(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Bonus).where(Bonus.status == BonusStatus.pending).order_by(Bonus.created_at.asc())
    bonuses = (await db.execute(q)).scalars().all()
    return [BonusOut.model_validate(b) for b in bonuses]
