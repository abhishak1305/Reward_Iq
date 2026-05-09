"""Rewards API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_admin, require_ownership_or_admin
from backend.models.reward import Reward
from backend.models.employee import Employee
from backend.models.user import User
from backend.schemas.reward import RewardCreate, RewardOut, RewardSummary

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.post("/", response_model=RewardOut, status_code=status.HTTP_201_CREATED)
async def assign_reward(
    payload: RewardCreate,
    token_data: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(Employee, payload.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")

    reward = Reward(  # type: ignore[call-arg]
        **payload.model_dump(),
        awarded_by=token_data.id,
    )
    db.add(reward)

    # Update employee points
    emp.reward_points += payload.points

    # Trigger Notification
    from backend.models.notification import Notification
    db.add(Notification(  # type: ignore[call-arg]
        user_id=emp.user_id,
        title=f"New Reward: {reward.title}",
        message=f"Congratulations! You've been awarded {payload.points} points. {payload.description or ''}",
        category="reward",
    ))

    await db.commit()
    await db.refresh(reward)
    return RewardOut.model_validate(reward)


@router.get("/employee/{employee_id}", response_model=list[RewardOut])
async def get_employee_rewards(
    employee_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Reward)
        .where(Reward.employee_id == employee_id)
        .order_by(Reward.awarded_at.desc())
        .offset(skip).limit(limit)
    )
    rewards = (await db.execute(q)).scalars().all()
    return [RewardOut.model_validate(r) for r in rewards]


@router.get("/employee/{employee_id}/summary", response_model=RewardSummary)
async def get_reward_summary(
    employee_id: int,
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    rewards = (
        await db.execute(
            select(Reward).where(Reward.employee_id == employee_id).order_by(Reward.awarded_at.desc())
        )
    ).scalars().all()

    total_points = sum(r.points for r in rewards)
    badge_count = sum(1 for r in rewards if r.reward_type.value == "badge")
    latest = RewardOut.model_validate(rewards[0]) if rewards else None

    return RewardSummary(
        total_points=total_points,
        total_rewards=len(rewards),
        badge_count=badge_count,
        latest_reward=latest,
    )


@router.get("/", response_model=list[RewardOut])
async def list_all_rewards(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Reward).order_by(Reward.awarded_at.desc()).offset(skip).limit(limit)
    rewards = (await db.execute(q)).scalars().all()
    return [RewardOut.model_validate(r) for r in rewards]
