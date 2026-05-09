"""Models package — re-export all models for Alembic auto-detection."""

from backend.models.user import User, UserRole
from backend.models.employee import Employee
from backend.models.attendance import Attendance, AttendanceStatus
from backend.models.reward import Reward, RewardType
from backend.models.bonus import Bonus, BonusStatus
from backend.models.feedback import Feedback
from backend.models.ai_prediction import AIPrediction
from backend.models.notification import Notification

__all__ = [
    "User", "UserRole",
    "Employee",
    "Attendance", "AttendanceStatus",
    "Reward", "RewardType",
    "Bonus", "BonusStatus",
    "Feedback",
    "AIPrediction",
    "Notification",
]
