"""SQLAlchemy ORM model — ai_predictions table."""

from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, Float, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "productivity", "reward_recommendation", "churn_risk", "sentiment_trend"
    score: Mapped[float | None] = mapped_column(Float)
    label: Mapped[str | None] = mapped_column(String(100))
    prediction_metadata: Mapped[dict | None] = mapped_column(JSON)  # flexible payload
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="ai_predictions")  # noqa: F821
