"""
Bias & Fairness Detection.

Detects statistical disparity in reward distribution across departments/groups.
Uses Statistical Parity Difference (SPD) and Disparate Impact (DI) metrics.
"""

import pandas as pd
import numpy as np
from typing import Any


def compute_fairness_report(reward_data: list[dict]) -> dict[str, Any]:
    """
    Compute fairness metrics from raw reward records.

    Each record: {employee_id, department, reward_points, productivity_score}
    """
    if len(reward_data) < 4:
        return {
            "overall_fairness_score": 1.0,
            "department_variance": {},
            "bias_flags": [],
            "recommendations": ["Insufficient data for fairness analysis."],
        }

    df = pd.DataFrame(reward_data)

    # Points per productivity ratio per department
    df["efficiency"] = np.where(df["productivity_score"] > 0, df["reward_points"] / df["productivity_score"], 0)

    dept_stats = df.groupby("department")["efficiency"].agg(["mean", "std"]).reset_index()
    dept_stats.columns = ["department", "mean_efficiency", "std_efficiency"]

    overall_mean = df["efficiency"].mean()
    dept_variance = {}
    bias_flags = []

    for _, row in dept_stats.iterrows():
        dept = row["department"]
        dept_mean = row["mean_efficiency"]
        ratio = dept_mean / max(overall_mean, 0.001)
        dept_variance[dept] = round(ratio, 3)

        if ratio < 0.75:
            bias_flags.append(f"⚠️ Department '{dept}' receives significantly fewer rewards relative to productivity.")
        elif ratio > 1.35:
            bias_flags.append(f"⚠️ Department '{dept}' may be over-rewarded relative to productivity.")

    # Overall fairness score: 1 - normalized variance across departments
    ratios = list(dept_variance.values())
    fairness_score = round(max(0, 1 - np.std(ratios)), 3) if len(ratios) > 1 else 1.0

    recommendations = []
    if fairness_score < 0.7:
        recommendations.append("Review reward allocation across departments for equity.")
    if bias_flags:
        recommendations.append("Investigate flagged departments and adjust reward policies.")
    if not recommendations:
        recommendations.append("Reward distribution appears fair across departments.")

    return {
        "overall_fairness_score": fairness_score,
        "department_variance": dept_variance,
        "bias_flags": bias_flags,
        "recommendations": recommendations,
    }
