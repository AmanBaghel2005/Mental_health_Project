"""
emotion_analysis.py
Maps face-api.js 7-class emotion distribution to a stress score.

face-api.js outputs: neutral, happy, sad, angry, fearful, disgusted, surprised
Each value is a float in [0, 1]; they sum to ~1.0.

Stress weights are grounded in the PANAS / DASS-21 valence-arousal literature:
  fearful  → highest stress marker (high arousal, very negative valence)
  angry    → high stress arousal
  sad      → depressive stress (low arousal, negative valence)
  disgusted→ negative affect
  surprised→ ambiguous arousal (context-dependent, mildly stressful)
  neutral  → baseline / minimal stress
  happy    → protective / inverse stress marker
"""
from typing import Dict, Optional

EMOTION_STRESS_WEIGHTS: Dict[str, float] = {
    "fearful":    0.90,
    "angry":      0.72,
    "sad":        0.62,
    "disgusted":  0.50,
    "surprised":  0.25,
    "neutral":    0.12,
    "happy":     -0.35,
}

_W_MIN = -0.35   # minimum possible weighted score (all happy)
_W_MAX =  0.90   # maximum possible weighted score (all fearful)


def compute_emotion_score(emotion_distribution: Optional[Dict[str, float]]) -> Dict:
    """
    Returns emotion stress score 0–100.
    0 = very positive / calm, 100 = highly stressed / fearful.
    """
    if not emotion_distribution:
        return {
            "emotion_score": 50.0,
            "dominant_emotion": "unknown",
            "emotion_distribution": {},
            "explanation": "No emotion data captured from camera.",
        }

    total = sum(emotion_distribution.values())
    if total == 0:
        return {
            "emotion_score": 50.0,
            "dominant_emotion": "unknown",
            "emotion_distribution": emotion_distribution,
            "explanation": "Emotion confidences are all zero.",
        }

    # Normalize to sum=1
    normed = {k: v / total for k, v in emotion_distribution.items()}

    # Weighted stress score
    raw = sum(
        EMOTION_STRESS_WEIGHTS.get(em, 0.12) * conf
        for em, conf in normed.items()
    )

    # Map [_W_MIN, _W_MAX] → [0, 100]
    emotion_score = (raw - _W_MIN) / (_W_MAX - _W_MIN) * 100.0
    emotion_score = max(0.0, min(100.0, emotion_score))

    dominant = max(normed, key=normed.get)
    dom_conf = normed[dominant]

    w = EMOTION_STRESS_WEIGHTS.get(dominant, 0.12)
    tone = ("high-stress" if w > 0.6 else
            "moderate-stress" if w > 0.25 else
            "stress-protective" if w < 0 else "neutral")

    explanation = (
        f"Dominant expression: {dominant} ({dom_conf*100:.0f}% confidence) — "
        f"classified as a {tone} indicator."
    )

    return {
        "emotion_score": round(emotion_score, 2),
        "dominant_emotion": dominant,
        "emotion_distribution": {k: round(v, 4) for k, v in normed.items()},
        "explanation": explanation,
    }
