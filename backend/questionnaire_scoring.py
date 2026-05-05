"""
questionnaire_scoring.py
Likert-scale scoring logic for the psychological questionnaire.

Scoring rules:
  - Negative question: score = selected_value (1-5)
  - Positive question:  score = 6 - selected_value  (inverted)
  - Max score per question = 5

Final percentage = (total_score / max_possible) * 100
Higher percentage = higher stress.
"""
from typing import List, Dict
from questionnaire_data import QUESTIONNAIRE

CATEGORY_LABELS = {
    "emotional": "Emotional Health",
    "social": "Social Well-being",
    "sleep": "Sleep Quality",
    "school": "School Stress",
    "focus": "Focus & Productivity",
    "future": "Future Anxiety",
    "interest": "Interest & Engagement",
    "work": "Work Stress",
    "financial": "Financial Stress",
    "motivation": "Motivation",
    "general": "General Well-being",
}


def score_single_question(q_type: str, selected_value: int) -> int:
    """
    Returns stress score for one question (1-5).
    Higher = more stressed.
    """
    val = max(1, min(5, selected_value))
    if q_type == "positive":
        return 6 - val   # Invert: strongly agree (5) → 1 stress
    else:
        return val        # Direct: strongly agree (5) → 5 stress


def compute_questionnaire_score(age_group: str, answers: List[int]) -> Dict:
    """
    Compute overall and category-wise stress scores from Likert answers.

    Args:
        age_group: "Child", "Youth", or "Adult"
        answers: List of integers (1-5), one per question in order

    Returns:
        Dict with total score, percentage, level, and category breakdown.
    """
    questions = QUESTIONNAIRE.get(age_group, [])
    if not questions:
        return {"error": f"Unknown age group: {age_group}"}

    n = len(questions)
    if len(answers) != n:
        return {"error": f"Expected {n} answers, got {len(answers)}"}

    max_possible = n * 5  # Each question max stress score = 5

    # Score each question
    scores = []
    category_scores: Dict[str, List[int]] = {}

    for i, q in enumerate(questions):
        s = score_single_question(q["type"], answers[i])
        scores.append(s)

        cat = q["category"]
        if cat not in category_scores:
            category_scores[cat] = []
        category_scores[cat].append(s)

    total_score = sum(scores)
    percentage = (total_score / max_possible) * 100.0

    # Stress level
    if percentage < 30:
        level = "Low"
    elif percentage < 60:
        level = "Moderate"
    else:
        level = "High"

    # Category breakdown
    categories = {}
    for cat, cat_scores in category_scores.items():
        cat_max = len(cat_scores) * 5
        cat_pct = (sum(cat_scores) / cat_max) * 100.0
        categories[cat] = {
            "label": CATEGORY_LABELS.get(cat, cat.title()),
            "score": sum(cat_scores),
            "max": cat_max,
            "percentage": round(cat_pct, 1),
        }

    return {
        "questionnaire_score": round(percentage, 2),
        "total_score": total_score,
        "max_possible": max_possible,
        "stress_level": level,
        "num_questions": n,
        "category_breakdown": categories,
    }
