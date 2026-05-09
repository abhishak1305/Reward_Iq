"""
Reward Recommender.

For small datasets (<50 employees), uses a content-based scoring fallback
using performance metrics → recommended reward type mapping.
"""

import numpy as np
import pandas as pd
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Reward type scoring weights (content-based fallback)
REWARD_RULES: list[dict[str, Any]] = [
    {
        "type": "bonus",
        "label": "💰 Performance Bonus",
        "condition": lambda p, a, s: p >= 80 and a >= 0.9,
        "priority": 1,
    },
    {
        "type": "badge",
        "label": "🏆 Achievement Badge",
        "condition": lambda p, a, s: p >= 70,
        "priority": 2,
    },
    {
        "type": "recognition",
        "label": "🌟 Public Recognition",
        "condition": lambda p, a, s: s >= 0.3,
        "priority": 3,
    },
    {
        "type": "extra_leave",
        "label": "🏖️ Extra Leave Day",
        "condition": lambda p, a, s: a >= 0.95,
        "priority": 4,
    },
    {
        "type": "gift_card",
        "label": "🎁 Gift Card",
        "condition": lambda p, a, s: p >= 60,
        "priority": 5,
    },
    {
        "type": "points",
        "label": "⭐ Reward Points",
        "condition": lambda p, a, s: True,
        "priority": 6,
    },
]


def recommend_for_employee(
    employee_id: int,
    productivity_score: float,
    attendance_rate: float,
    avg_sentiment: float,
    reward_history: list[str] | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Generate top-k reward recommendations for an employee.
    Returns recommended rewards and a human-readable reasoning string.
    """
    history = set(reward_history or [])

    scored: list[dict] = []
    for rule in REWARD_RULES:
        try:
            qualifies = rule["condition"](productivity_score, attendance_rate, avg_sentiment)
        except Exception:
            qualifies = False

        if qualifies:
            # Boost if not yet received this type
            novelty_bonus = 1.0 if rule["type"] not in history else 0.7
            scored.append({
                "type": rule["type"],
                "label": rule["label"],
                "score": novelty_bonus * (7 - rule["priority"]),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:top_k]

    # Build reasoning
    parts = []
    if productivity_score >= 80:
        parts.append(f"high productivity ({productivity_score:.0f}/100)")
    if attendance_rate >= 0.9:
        parts.append(f"excellent attendance ({attendance_rate*100:.0f}%)")
    if avg_sentiment >= 0.3:
        parts.append("positive team feedback")

    reasoning = (
        f"Recommended based on: {', '.join(parts)}." if parts
        else "Recommended as a motivational reward to improve engagement."
    )

    return {
        "employee_id": employee_id,
        "recommended_rewards": top,
        "reasoning": reasoning,
    }


def batch_recommend(employees: list[dict], top_k: int = 3) -> list[dict]:
    """Generate recommendations for a list of employee data dicts."""
    return [
        recommend_for_employee(
            employee_id=e["id"],
            productivity_score=e.get("productivity_score", 0),
            attendance_rate=e.get("attendance_rate", 0),
            avg_sentiment=e.get("avg_sentiment", 0),
            reward_history=e.get("reward_history", []),
            top_k=top_k,
        )
        for e in employees
    ]
