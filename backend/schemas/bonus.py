"""Pydantic v2 schemas for Bonuses."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from backend.models.bonus import BonusStatus


class BonusCreate(BaseModel):
    employee_id: int
    amount: float = Field(gt=0)
    reason: str = Field(min_length=5)


class BonusReview(BaseModel):
    status: BonusStatus  # approved | rejected
    rejection_note: Optional[str] = None


class BonusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    amount: float
    reason: str
    status: BonusStatus
    requested_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_note: Optional[str]
    created_at: datetime
    updated_at: datetime
