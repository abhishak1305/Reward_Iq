"""SQLAlchemy ORM model — rewards table."""

from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.core.database import Base


class RewardType(str, enum.Enum):
    points = "points"
    badge = "badge"
    bonus = "bonus"
    recognition = "recognition"
    gift_card = "gift_card"
    extra_leave = "extra_leave"


class Reward(Base):
    __tablename__ = "rewards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    awarded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_type: Mapped[RewardType] = mapped_column(Enum(RewardType), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    badge_icon: Mapped[str | None] = mapped_column(String(100))  # icon name/emoji
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="rewards")  # noqa: F821
