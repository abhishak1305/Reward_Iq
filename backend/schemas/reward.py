"""Pydantic v2 schemas for Rewards."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from backend.models.reward import RewardType


class RewardCreate(BaseModel):
    employee_id: int
    reward_type: RewardType
    points: int = Field(ge=0, default=0)
    title: str = Field(min_length=2, max_length=255)
    description: Optional[str] = None
    badge_icon: Optional[str] = None


class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    awarded_by: int
    reward_type: RewardType
    points: int
    title: str
    description: Optional[str]
    badge_icon: Optional[str]
    awarded_at: datetime


class RewardSummary(BaseModel):
    total_points: int
    total_rewards: int
    badge_count: int
    latest_reward: Optional[RewardOut] = None
