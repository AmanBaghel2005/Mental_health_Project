"""
blink_analysis.py
Scores blink rate data (sent from MediaPipe FaceMesh in browser) against
clinically validated normal ranges.

Normal range : 12–20 BPM  (Patel et al. 2021)
Stress-high  : >25 BPM   (anxiety / nervousness)
Stress-low   : <8  BPM   (fatigue / dissociation)
"""
from typing import Dict

NORMAL_LOW  = 12.0
NORMAL_HIGH = 20.0
STRESS_HIGH = 25.0
STRESS_LOW  = 8.0


def compute_blink_score(
    blink_count: int,
    session_duration_s: float,
    blink_rate_bpm: float = None,
) -> Dict:
    """
    Returns blink anomaly score 0–100 (0 = normal pattern, 100 = highly anomalous).
    """
    # Derive BPM when not pre-computed
    if blink_rate_bpm is None:
        minutes = max(session_duration_s / 60.0, 0.01)
        blink_rate_bpm = blink_count / minutes

    # Not enough data
    if blink_count == 0 or session_duration_s < 15:
        return {
            "blink_score": 50.0,
            "blink_status": "no_data",
            "blink_rate_bpm": 0.0,
            "explanation": "Insufficient blink data collected — visual signal excluded.",
        }

    bpm = blink_rate_bpm

    if bpm < STRESS_LOW:
        severity = (STRESS_LOW - bpm) / STRESS_LOW
        score = 70 + severity * 30
        status = "very_low"
        explanation = (
            f"Very low blink rate ({bpm:.1f}/min) suggests fatigue or reduced alertness. "
            f"Normal range: {NORMAL_LOW}–{NORMAL_HIGH}/min."
        )
    elif bpm > STRESS_HIGH:
        severity = min((bpm - STRESS_HIGH) / STRESS_HIGH, 1.0)
        score = 70 + severity * 30
        status = "very_high"
        explanation = (
            f"High blink rate ({bpm:.1f}/min) may indicate anxiety or nervousness. "
            f"Normal range: {NORMAL_LOW}–{NORMAL_HIGH}/min."
        )
    elif bpm < NORMAL_LOW:
        frac = (NORMAL_LOW - bpm) / (NORMAL_LOW - STRESS_LOW)
        score = frac * 45
        status = "below_normal"
        explanation = f"Blink rate slightly below normal ({bpm:.1f}/min)."
    elif bpm > NORMAL_HIGH:
        frac = (bpm - NORMAL_HIGH) / (STRESS_HIGH - NORMAL_HIGH)
        score = frac * 45
        status = "above_normal"
        explanation = f"Blink rate slightly above normal ({bpm:.1f}/min)."
    else:
        score = 5.0
        status = "normal"
        explanation = f"Blink rate ({bpm:.1f}/min) is within the normal range."

    return {
        "blink_score": round(min(100.0, max(0.0, score)), 2),
        "blink_status": status,
        "blink_rate_bpm": round(bpm, 2),
        "explanation": explanation,
    }
