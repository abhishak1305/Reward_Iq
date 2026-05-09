"""Feedback API router with auto sentiment analysis."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_ownership_or_admin
from backend.models.feedback import Feedback
from backend.schemas.ai import FeedbackCreate, FeedbackOut
from backend.ai.sentiment import analyze_sentiment, aggregate_sentiment

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Auto-run sentiment analysis
    sentiment = analyze_sentiment(payload.content)

    fb = Feedback(  # type: ignore[call-arg]
        employee_id=payload.employee_id,
        submitted_by=user_id,
        content=payload.content,
        category=payload.category,
        sentiment_score=sentiment.score,
        sentiment_label=sentiment.label,
    )
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return FeedbackOut.model_validate(fb)


@router.get("/employee/{employee_id}", response_model=list[FeedbackOut])
async def get_employee_feedback(
    employee_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Feedback)
        .where(Feedback.employee_id == employee_id)
        .order_by(Feedback.created_at.desc())
        .offset(skip).limit(limit)
    )
    items = (await db.execute(q)).scalars().all()
    return [FeedbackOut.model_validate(f) for f in items]


@router.get("/employee/{employee_id}/sentiment")
async def get_sentiment_summary(
    employee_id: int,
    _=Depends(require_ownership_or_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(Feedback).where(Feedback.employee_id == employee_id)
    items = (await db.execute(q)).scalars().all()
    from backend.schemas.ai import SentimentResult
    results = [
        SentimentResult(
            score=f.sentiment_score or 0,
            label=f.sentiment_label or "neutral",
            compound=f.sentiment_score or 0,
        )
        for f in items if f.sentiment_score is not None
    ]
    return aggregate_sentiment(results)
