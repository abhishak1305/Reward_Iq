"""
Sentiment Analysis using VADER + TextBlob ensemble.

VADER is ideal for short business feedback (calibrated for social text).
TextBlob provides a secondary polarity signal.
Final score is a weighted average.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from backend.schemas.ai import SentimentResult

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Analyse a feedback text string and return sentiment score + label.

    Score range: -1.0 (very negative) → 1.0 (very positive)
    """
    # VADER score (compound: -1 to 1)
    vader_scores = _analyzer.polarity_scores(text)
    vader_compound = vader_scores["compound"]

    # TextBlob polarity (-1 to 1)
    blob_polarity = TextBlob(text).sentiment.polarity

    # Weighted ensemble: VADER 70%, TextBlob 30%
    final_score = round(0.7 * vader_compound + 0.3 * blob_polarity, 4)

    # Label
    if final_score >= 0.05:
        label = "positive"
    elif final_score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return SentimentResult(
        score=final_score,
        label=label,
        compound=vader_compound,
    )


def batch_analyze(texts: list[str]) -> list[SentimentResult]:
    """Analyse multiple texts and return results in the same order."""
    return [analyze_sentiment(t) for t in texts]


def aggregate_sentiment(results: list[SentimentResult]) -> dict:
    """Compute aggregate stats from a list of sentiment results."""
    if not results:
        return {"average_score": 0.0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0}

    scores = [r.score for r in results]
    labels = [r.label for r in results]
    n = len(labels)

    return {
        "average_score": round(sum(scores) / n, 4),
        "positive_pct": round(labels.count("positive") / n * 100, 1),
        "neutral_pct": round(labels.count("neutral") / n * 100, 1),
        "negative_pct": round(labels.count("negative") / n * 100, 1),
        "count": n,
    }
