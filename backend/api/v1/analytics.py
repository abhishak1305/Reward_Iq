"""Analytics API router — aggregated dashboard metrics."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, String

from backend.core.database import get_db
from backend.core.security import require_admin
from backend.models.employee import Employee
from backend.models.attendance import Attendance, AttendanceStatus
from backend.models.reward import Reward
from backend.models.bonus import Bonus, BonusStatus
from backend.models.feedback import Feedback

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """High-level KPI summary for the admin dashboard."""
    total_employees = await db.scalar(select(func.count(Employee.id)))
    total_rewards = await db.scalar(select(func.count(Reward.id)))
    total_points = await db.scalar(select(func.coalesce(func.sum(Employee.reward_points), 0)))
    pending_bonuses = await db.scalar(
        select(func.count(Bonus.id)).where(Bonus.status == BonusStatus.pending)
    )
    avg_productivity = await db.scalar(
        select(func.round(func.avg(Employee.productivity_score), 2))
    )
    total_feedback = await db.scalar(select(func.count(Feedback.id)))

    return {
        "total_employees": total_employees or 0,
        "total_rewards_given": total_rewards or 0,
        "total_reward_points": int(total_points or 0),
        "pending_bonuses": pending_bonuses or 0,
        "avg_productivity_score": float(avg_productivity or 0),
        "total_feedback_entries": total_feedback or 0,
    }


@router.get("/department-performance")
async def get_department_performance(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Avg productivity and reward points per department."""
    q = select(
        Employee.department,
        func.count(Employee.id).label("count"),
        func.round(func.avg(Employee.productivity_score), 2).label("avg_productivity"),
        func.round(func.avg(Employee.reward_points), 0).label("avg_points"),
    ).group_by(Employee.department)
    rows = (await db.execute(q)).all()
    return [
        {
            "department": r.department,
            "employee_count": r.count,
            "avg_productivity": float(r.avg_productivity or 0),
            "avg_reward_points": float(r.avg_points or 0),
        }
        for r in rows
    ]


@router.get("/attendance-trend")
async def get_attendance_trend(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Monthly attendance rates for the past 6 months."""
    # Use strftime for SQLite or to_char for Postgres if we were there
    # For now, keeping it robust for SQLite as per project defaults
    month_expr = func.strftime("%Y-%m", Attendance.date)
    
    q = (
        select(
            month_expr.label("month"),
            func.count(Attendance.id).label("total"),
            func.sum(
                func.case(
                    (Attendance.status.in_([AttendanceStatus.present, AttendanceStatus.remote, AttendanceStatus.half_day]), 1),
                    else_=0,
                )
            ).label("present"),
        )
        .group_by(month_expr)
        .order_by(month_expr.desc())
        .limit(6)
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    # Map and reverse to show chronological order on chart
    trend = []
    for r in reversed(rows):
        total = int(r.total or 0)
        present = int(r.present or 0)
        trend.append({
            "month": str(r.month) if r.month else "Unknown",
            "attendance_rate": round(present / total, 3) if total > 0 else 0,
            "total": total,
        })
    return trend


@router.get("/reward-distribution")
async def get_reward_distribution(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Reward type distribution counts."""
    q = select(Reward.reward_type, func.count(Reward.id).label("count")).group_by(Reward.reward_type)
    rows = (await db.execute(q)).all()
    return [{"type": r.reward_type.value, "count": r.count} for r in rows]
