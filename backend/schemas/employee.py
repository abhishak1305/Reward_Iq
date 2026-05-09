"""Pydantic v2 schemas for Employee."""

from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional


class EmployeeBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    department: str = Field(min_length=2, max_length=100)
    position: str = Field(min_length=2, max_length=100)
    hire_date: date
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    user_id: int


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class EmployeeOut(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    reward_points: int
    productivity_score: float
    created_at: datetime
    updated_at: datetime


class EmployeeWithEmail(EmployeeOut):
    email: str
    role: str


class EmployeeRankItem(BaseModel):
    rank: int
    employee_id: int
    full_name: str
    department: str
    reward_points: int
    productivity_score: float
