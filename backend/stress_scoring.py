"""
stress_scoring.py
Combines three independent stress signals into a single final score.

Weights:
  questionnaire 40% — self-report Likert scale, strongest predictor
  emotion       30% — objective facial signal from face-api.js
  blink         30% — physiological EAR blink pattern from MediaPipe

Risk thresholds approximate PHQ-9 / GAD-7 severity bands.
"""
from typing import Dict

WEIGHTS = {"questionnaire": 0.40, "emotion": 0.30, "blink": 0.30}


def compute_final_stress_score(
    questionnaire_score: float,
    emotion_score: float,
    blink_score: float,
    questionnaire_explanation: str = "",
    emotion_explanation: str = "",
    blink_explanation: str = "",
) -> Dict:
    """
    Returns final risk assessment dict.
    All inputs are 0-100 stress scores (higher = more stressed).
    """
    final = (
        questionnaire_score * WEIGHTS["questionnaire"] +
        emotion_score       * WEIGHTS["emotion"] +
        blink_score         * WEIGHTS["blink"]
    )
    final = round(max(0.0, min(100.0, final)), 2)

    if final < 30:
        level = "Low"
        rec = (
            "Your indicators suggest you are managing well. "
            "Keep practising self-care, staying connected, and maintaining healthy sleep habits."
        )
    elif final < 55:
        level = "Mild"
        rec = (
            "You may be experiencing mild stress. Consider mindfulness exercises, "
            "short breaks, and talking to someone you trust."
        )
    elif final < 75:
        level = "Moderate"
        rec = (
            "Your signals indicate moderate stress levels. It would be beneficial to speak "
            "with a counsellor or mental health professional for a structured check-in."
        )
    else:
        level = "Elevated"
        rec = (
            "Your indicators suggest elevated stress or distress. "
            "We strongly recommend reaching out to a licensed mental health professional "
            "or calling a mental health helpline."
        )

    # Build human-readable explanation
    parts = []
    if questionnaire_explanation:
        parts.append(f"• Questionnaire: {questionnaire_explanation}")
    if emotion_explanation:
        parts.append(f"• Facial emotion: {emotion_explanation}")
    if blink_explanation:
        parts.append(f"• Blink pattern: {blink_explanation}")

    return {
        "risk_score": final,
        "risk_level": level,
        "recommendation": rec,
        "score_breakdown": {
            "questionnaire_score": round(questionnaire_score, 2),
            "emotion_stress_score": round(emotion_score, 2),
            "blink_anomaly_score": round(blink_score, 2),
            "weights": WEIGHTS,
        },
        "explanation": "\n".join(parts),
    }
