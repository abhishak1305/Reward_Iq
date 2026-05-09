"""SQLAlchemy ORM model — attendance table."""

from datetime import date, time, datetime
from sqlalchemy import String, Date, Time, ForeignKey, DateTime, func, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.core.database import Base


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    half_day = "half_day"
    remote = "remote"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (Index("ix_attendance_emp_date", "employee_id", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[time | None] = mapped_column(Time)
    check_out: Mapped[time | None] = mapped_column(Time)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_records")  # noqa: F821
