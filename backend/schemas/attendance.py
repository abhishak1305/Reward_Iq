"""Pydantic v2 schemas for Attendance."""

from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from backend.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: AttendanceStatus
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    date: date
    check_in: Optional[time]
    check_out: Optional[time]
    status: AttendanceStatus
    notes: Optional[str]
    created_at: datetime


class AttendanceSummary(BaseModel):
    employee_id: int
    total_days: int
    present: int
    absent: int
    late: int
    half_day: int
    remote: int
    attendance_rate: float
