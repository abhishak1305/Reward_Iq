"""Attendance tracking API router."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_admin, require_ownership_or_admin
from backend.models.attendance import Attendance, AttendanceStatus
from backend.models.employee import Employee
from backend.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceOut, AttendanceSummary

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    payload: AttendanceCreate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Prevent duplicate entry for same employee+date
    existing = await db.scalar(
        select(Attendance).where(
            and_(Attendance.employee_id == payload.employee_id, Attendance.date == payload.date)
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Attendance already recorded for this date.")

    record = Attendance(**payload.model_dump())  # type: ignore[call-arg]
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return AttendanceOut.model_validate(record)


@router.get("/employee/{employee_id}", response_model=list[AttendanceOut])
async def get_employee_attendance(
    employee_id: int,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Attendance).where(Attendance.employee_id == employee_id)
    if from_date:
        q = q.where(Attendance.date >= from_date)
    if to_date:
        q = q.where(Attendance.date <= to_date)
    q = q.order_by(Attendance.date.desc())
    records = (await db.execute(q)).scalars().all()
    return [AttendanceOut.model_validate(r) for r in records]


@router.get("/employee/{employee_id}/summary", response_model=AttendanceSummary)
async def get_attendance_summary(
    employee_id: int,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Attendance).where(Attendance.employee_id == employee_id)
    if from_date:
        q = q.where(Attendance.date >= from_date)
    if to_date:
        q = q.where(Attendance.date <= to_date)
    records = (await db.execute(q)).scalars().all()

    counts = {s.value: 0 for s in AttendanceStatus}
    for r in records:
        counts[r.status.value] += 1

    total = len(records)
    present = counts["present"] + counts["remote"] + counts["half_day"]

    return AttendanceSummary(
        employee_id=employee_id,
        total_days=total,
        present=counts["present"],
        absent=counts["absent"],
        late=counts["late"],
        half_day=counts["half_day"],
        remote=counts["remote"],
        attendance_rate=round(present / total, 4) if total else 0.0,
    )


@router.patch("/{record_id}", response_model=AttendanceOut)
async def update_attendance(
    record_id: int,
    payload: AttendanceUpdate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    record = await db.get(Attendance, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")
    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(record, field, val)
    await db.commit()
    await db.refresh(record)
    return AttendanceOut.model_validate(record)
