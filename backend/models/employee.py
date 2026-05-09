"""SQLAlchemy ORM model — employees table."""

from datetime import date, datetime
from sqlalchemy import String, Date, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    reward_points: Mapped[int] = mapped_column(default=0, nullable=False)
    productivity_score: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="employee")  # noqa: F821
    attendance_records: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="employee", cascade="all, delete-orphan"
    )  # noqa: F821
    rewards: Mapped[list["Reward"]] = relationship(
        "Reward", back_populates="employee", cascade="all, delete-orphan"
    )  # noqa: F821
    bonuses: Mapped[list["Bonus"]] = relationship(
        "Bonus", back_populates="employee", cascade="all, delete-orphan"
    )  # noqa: F821
    feedback_entries: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="employee", cascade="all, delete-orphan"
    )  # noqa: F821
    ai_predictions: Mapped[list["AIPrediction"]] = relationship(
        "AIPrediction", back_populates="employee", cascade="all, delete-orphan"
    )  # noqa: F821
