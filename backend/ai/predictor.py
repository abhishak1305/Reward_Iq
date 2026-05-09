"""
Productivity Predictor using RandomForest Regressor.

Features used:
  - attendance_rate       (float, 0-1)
  - avg_sentiment_score   (float, -1 to 1)
  - reward_points         (int)
  - days_since_hire       (int)
  - feedback_count        (int)

Target: productivity_score (0-100)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "artifacts", "productivity_model.pkl")

_cached_pipeline = None
_last_mtime = 0

def _get_pipeline():
    global _cached_pipeline, _last_mtime
    if os.path.exists(MODEL_PATH):
        mtime = os.path.getmtime(MODEL_PATH)
        if _cached_pipeline is None or mtime > _last_mtime:
            _cached_pipeline = joblib.load(MODEL_PATH)
            _last_mtime = mtime
    return _cached_pipeline

FEATURES = [
    "attendance_rate",
    "avg_sentiment_score",
    "reward_points",
    "days_since_hire",
    "feedback_count",
]


def _build_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )),
    ])


def train(data: list[dict]) -> None:
    """
    Train the productivity predictor on a list of employee feature dicts.
    Each dict must contain FEATURES keys plus a 'productivity_score' key.
    """
    if len(data) < 5:
        logger.warning("Insufficient data for training (%d samples). Need ≥5.", len(data))
        return

    df = pd.DataFrame(data)
    X = df[FEATURES].fillna(0)
    y = df["productivity_score"].clip(0, 100)

    pipeline = _build_pipeline()
    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("Productivity model trained and saved (%d samples).", len(df))


def predict(features: dict) -> dict:
    """
    Predict productivity score for a single employee.
    Falls back to rule-based heuristic if model not trained.
    """
    pipeline = _get_pipeline()
    if pipeline is not None:
        try:
            X = pd.DataFrame([{f: features.get(f, 0) for f in FEATURES}])
            
            # Use standard deviation across trees to estimate confidence
            rf: RandomForestRegressor = pipeline.named_steps["model"]
            X_scaled = pipeline.named_steps["scaler"].transform(X)
            preds = np.array([tree.predict(X_scaled)[0] for tree in rf.estimators_])
            
            score = float(preds.mean())
            score = round(min(max(score, 0), 100), 2)
            
            std_dev = float(preds.std())
            confidence = round(max(0.0, 1.0 - (std_dev / 20.0)), 2)

            # Feature importances for explanation
            importances = dict(zip(FEATURES, rf.feature_importances_.tolist()))

            return {
                "predicted_score": score,
                "confidence": confidence,
                "factors": importances,
                "method": "ml",
            }
        except Exception as e:
            logger.warning("ML prediction failed (%s), using heuristic.", e)

    # Rule-based fallback
    att = features.get("attendance_rate", 0.8)
    sent = features.get("avg_sentiment_score", 0)
    pts = min(features.get("reward_points", 0) / 500, 1.0)
    score = round((att * 50 + (sent + 1) / 2 * 30 + pts * 20), 2)

    return {
        "predicted_score": score,
        "confidence": 0.60,
        "factors": {
            "attendance_rate": 0.5,
            "avg_sentiment_score": 0.3,
            "reward_points": 0.2,
        },
        "method": "heuristic",
    }
