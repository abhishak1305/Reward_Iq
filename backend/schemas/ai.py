"""Pydantic v2 schemas for Feedback and AI predictions."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any


# ── Feedback ──────────────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    employee_id: int
    content: str = Field(min_length=10)
    category: str = "general"


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    submitted_by: int
    content: str
    category: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    created_at: datetime


# ── AI Predictions ────────────────────────────────────────────────────────────

class AIPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    prediction_type: str
    score: Optional[float]
    label: Optional[str]
    prediction_metadata: Optional[dict[str, Any]]
    model_version: str
    created_at: datetime


class SentimentResult(BaseModel):
    score: float  # -1.0 to 1.0
    label: str    # positive | neutral | negative
    compound: float


class ProductivityPrediction(BaseModel):
    employee_id: int
    predicted_score: float
    confidence: float
    factors: dict[str, float]


class RewardRecommendation(BaseModel):
    employee_id: int
    recommended_rewards: list[dict[str, Any]]
    reasoning: str


class FairnessReport(BaseModel):
    overall_fairness_score: float
    department_variance: dict[str, float]
    bias_flags: list[str]
    recommendations: list[str]


class EmployeeInsight(BaseModel):
    employee_id: int
    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    trend: str  # improving | stable | declining
