"""SQLAlchemy ORM model — feedback table."""

from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, Float, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")

    # AI-computed fields
    sentiment_score: Mapped[float | None] = mapped_column(Float)  # -1.0 to 1.0
    sentiment_label: Mapped[str | None] = mapped_column(String(20))  # positive/neutral/negative

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="feedback_entries")  # noqa: F821
