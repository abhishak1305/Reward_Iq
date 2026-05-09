"""AI predictions API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_admin
from backend.models.employee import Employee
from backend.models.attendance import Attendance, AttendanceStatus
from backend.models.feedback import Feedback
from backend.models.reward import Reward
from backend.models.ai_prediction import AIPrediction
from backend.ai import sentiment as sentiment_mod, predictor, recommender, fairness, insights

router = APIRouter(prefix="/ai", tags=["ai"])


async def _get_employee_features(employee_id: int, db: AsyncSession) -> dict:
    """Assemble feature dict for an employee."""
    query = (
        select(
            Employee,
            func.count(Attendance.id.distinct()).label("total_att"),
            func.sum(
                case((Attendance.status.in_([AttendanceStatus.present, AttendanceStatus.remote, AttendanceStatus.half_day]), 1), else_=0)  # type: ignore[arg-type]
            ).label("present_att"),
            func.count(Feedback.id.distinct()).label("total_fb"),
            func.avg(Feedback.sentiment_score).label("avg_sent")
        )
        .outerjoin(Attendance, Attendance.employee_id == Employee.id)
        .outerjoin(Feedback, Feedback.employee_id == Employee.id)
        .where(Employee.id == employee_id)
        .group_by(Employee.id)
    )
    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found.")

    emp = result[0]
    total_att = result.total_att or 0
    present_att = result.present_att or 0
    att_rate = float(present_att) / float(total_att) if total_att > 0 else 0.8
    total_fb = result.total_fb or 0
    avg_sent = float(result.avg_sent) if result.avg_sent is not None else 0.0

    from datetime import date
    hire_delta = (date.today() - emp.hire_date).days

    return {
        "id": emp.id,
        "full_name": emp.full_name,
        "attendance_rate": att_rate,
        "avg_sentiment_score": avg_sent,
        "reward_points": emp.reward_points,
        "days_since_hire": hire_delta,
        "feedback_count": total_fb,
        "productivity_score": emp.productivity_score,
    }


@router.get("/predict/productivity/{employee_id}")
async def predict_productivity(
    employee_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    features = await _get_employee_features(employee_id, db)
    result = predictor.predict(features)

    # Persist prediction
    pred = AIPrediction(  # type: ignore[call-arg]
        employee_id=employee_id,
        prediction_type="productivity",
        score=result["predicted_score"],
        label="high" if result["predicted_score"] >= 75 else "medium" if result["predicted_score"] >= 50 else "low",
        prediction_metadata=result,
    )
    db.add(pred)
    await db.commit()
    return {**result, "employee_id": employee_id}


@router.get("/recommend/rewards/{employee_id}")
async def get_reward_recommendations(
    employee_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    features = await _get_employee_features(employee_id, db)
    reward_history = (await db.execute(
        select(Reward.reward_type).where(Reward.employee_id == employee_id)
    )).scalars().all()
    history = [r.value for r in reward_history]

    result = recommender.recommend_for_employee(
        employee_id=employee_id,
        productivity_score=features["productivity_score"],
        attendance_rate=features["attendance_rate"],
        avg_sentiment=features["avg_sentiment_score"],
        reward_history=history,
    )
    return result


@router.get("/insights/{employee_id}")
async def get_employee_insights(
    employee_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    features = await _get_employee_features(employee_id, db)
    # Get productivity trend (last 10 predictions)
    preds = (await db.execute(
        select(AIPrediction)
        .where(AIPrediction.employee_id == employee_id, AIPrediction.prediction_type == "productivity")
        .order_by(AIPrediction.created_at.asc())
        .limit(10)
    )).scalars().all()
    trend = [p.score for p in preds if p.score is not None]
    features["productivity_trend"] = trend

    return insights.generate_employee_insight(features)


@router.get("/fairness")
async def get_fairness_report(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    employees = (await db.execute(
        select(Employee.id, Employee.department, Employee.reward_points, Employee.productivity_score)
    )).all()
    data = [
        {
            "employee_id": e.id,
            "department": e.department,
            "reward_points": e.reward_points,
            "productivity_score": e.productivity_score,
        }
        for e in employees
    ]
    return fairness.compute_fairness_report(data)


@router.get("/sentiment/org")
async def get_org_sentiment(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Organisation-wide sentiment summary."""
    all_feedback = (await db.execute(
        select(Feedback.sentiment_score, Feedback.sentiment_label)
        .where(Feedback.sentiment_score.isnot(None))
    )).all()
    from backend.schemas.ai import SentimentResult
    results = [
        SentimentResult(score=f.sentiment_score, label=f.sentiment_label or "neutral", compound=f.sentiment_score)
        for f in all_feedback
    ]
    return sentiment_mod.aggregate_sentiment(results)
