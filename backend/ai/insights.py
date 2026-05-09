"""
Employee Insight Generator.

Produces human-readable insights by combining attendance, sentiment,
productivity, and reward data into a structured profile.
"""

from typing import Any


def generate_employee_insight(data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate a structured insight for a single employee.

    data keys:
        employee_id, full_name, productivity_score, attendance_rate,
        avg_sentiment_score, reward_points, feedback_count,
        productivity_trend (list of scores, oldest→newest)
    """
    name = data.get("full_name", "This employee")
    prod = data.get("productivity_score", 0)
    att = data.get("attendance_rate", 0)
    sent = data.get("avg_sentiment_score", 0)
    pts = data.get("reward_points", 0)
    trend_list: list[float] = data.get("productivity_trend", [])

    # Trend direction
    if len(trend_list) >= 3:
        recent_avg = sum(trend_list[-3:]) / 3
        older_avg = sum(trend_list[:-3]) / max(len(trend_list) - 3, 1)
        if recent_avg > older_avg + 5:
            trend = "improving"
        elif recent_avg < older_avg - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Strengths
    strengths: list[str] = []
    if att >= 0.95:
        strengths.append("Exceptional attendance and reliability")
    elif att >= 0.85:
        strengths.append("Consistent attendance record")
    if prod >= 80:
        strengths.append("High productivity performer")
    if sent >= 0.4:
        strengths.append("Very positive feedback from peers")
    elif sent >= 0.1:
        strengths.append("Generally positive peer sentiment")
    if pts >= 500:
        strengths.append("Strong reward track record")
    if not strengths:
        strengths.append("Shows potential for growth")

    # Areas for improvement
    areas: list[str] = []
    if att < 0.75:
        areas.append("Attendance consistency needs improvement")
    if prod < 60:
        areas.append("Focus on productivity-boosting habits")
    if sent < -0.1:
        areas.append("Peer feedback suggests interpersonal friction")
    if trend == "declining":
        areas.append("Recent performance trend is declining — early intervention recommended")
    if not areas:
        areas.append("Continue maintaining current performance levels")

    # Summary
    trend_phrase = {"improving": "📈 on an upward trajectory", "declining": "📉 showing a downward trend", "stable": "➡️ maintaining a steady pace"}
    summary = (
        f"{name} is {trend_phrase[trend]} with a productivity score of {prod:.0f}/100 "
        f"and an attendance rate of {att*100:.0f}%. "
        f"Peer sentiment is {'positive' if sent >= 0.05 else 'neutral' if sent > -0.05 else 'negative'} "
        f"with {pts} reward points accumulated."
    )

    return {
        "employee_id": data.get("employee_id"),
        "summary": summary,
        "strengths": strengths,
        "areas_for_improvement": areas,
        "trend": trend,
    }


def generate_batch_insights(employees: list[dict]) -> list[dict]:
    return [generate_employee_insight(e) for e in employees]
