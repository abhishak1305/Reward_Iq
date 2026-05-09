"""API v1 router — aggregates all sub-routers."""

from fastapi import APIRouter
from backend.api.v1 import auth, employees, attendance, rewards, bonuses, feedback, analytics, ai_predictions, notifications, chatbot

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(employees.router)
router.include_router(attendance.router)
router.include_router(rewards.router)
router.include_router(bonuses.router)
router.include_router(feedback.router)
router.include_router(analytics.router)
router.include_router(ai_predictions.router)
router.include_router(notifications.router)
router.include_router(chatbot.router)
