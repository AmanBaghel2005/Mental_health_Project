"""
ai_logic.py
NLP-based text stress analysis using VADER + a curated stress/wellness lexicon.

VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon-based
sentiment analyser validated on social media text — well-suited to short,
informal answers like those collected in this assessment.

The custom stress lexicon augments VADER with 60+ clinically relevant terms
mapped to their stress contribution weight.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict

# ── Questions ────────────────────────────────────────────────────────────────
QUESTIONS = {
    "Under 18": [
        "How do you feel about your studies these days?",
        "Do you feel stressed because of school or exams?",
        "Are you able to concentrate properly while studying?",
        "Do you feel tired even after resting?",
        "Do you enjoy playing or spending time with friends?",
        "Do you feel pressure from parents or teachers?",
        "How is your sleep routine lately?",
        "Do you feel nervous before tests or classes?",
        "Do you feel happy doing your daily activities?",
        "Do you feel distracted easily while studying?",
    ],
    "Youth": [
        "How has your mood been recently?",
        "Do you feel mentally exhausted or tired?",
        "Are you able to focus on your work or studies?",
        "Do you feel stressed about your future or career?",
        "How is your sleep quality these days?",
        "Do you feel socially active or withdrawn?",
        "Do you feel overwhelmed by daily responsibilities?",
        "Do you feel motivated to complete your tasks?",
        "Do you feel anxious or overthinking often?",
        "Do you feel emotionally stable most of the time?",
    ],
    "Adult": [
        "Do you feel stressed in your daily life?",
        "Do you feel low or unmotivated frequently?",
        "Are you able to concentrate on your work?",
        "How is your sleep pattern recently?",
        "Do you feel mentally tired even after rest?",
        "Do you feel socially connected or isolated?",
        "Do you feel pressure from work or responsibilities?",
        "Do you feel anxious or worried often?",
        "Do you feel satisfied with your daily routine?",
        "Do you feel emotionally balanced most of the time?",
    ],
}

# ── Stress Lexicon ────────────────────────────────────────────────────────────
# Positive values increase the stress score; negative values decrease it.
# Values are additive deltas applied to the baseline score per word hit.
STRESS_LEXICON: Dict[str, float] = {
    # High-stress terms
    "anxious": 2.2, "anxiety": 2.2, "overwhelmed": 2.5, "exhausted": 2.0,
    "depressed": 2.8, "depression": 2.8, "hopeless": 3.0, "worthless": 2.8,
    "panic": 2.5, "panicking": 2.5, "dread": 2.2, "suffer": 2.0,
    "terrible": 1.8, "horrible": 1.8, "miserable": 2.2, "stressed": 2.0,
    "burden": 1.8, "lonely": 1.8, "isolated": 1.8, "scared": 1.8,
    "worried": 1.8, "nervous": 1.6, "tense": 1.4, "tired": 1.2,
    "sleepless": 1.8, "insomnia": 1.8, "crying": 1.8, "unmotivated": 1.5,
    "distracted": 1.2, "withdrawn": 1.5, "frustrated": 1.6, "hate": 1.4,
    "failing": 1.8, "fail": 1.5, "fear": 1.8, "afraid": 1.8,
    "pressure": 1.4, "struggle": 1.6, "struggling": 1.6, "helpless": 2.2,
    "numb": 1.6, "empty": 1.8, "restless": 1.4, "overthinking": 2.0,
    "breakdown": 2.5, "burnout": 2.5,
    # Wellness/protective terms
    "happy": -1.8, "happiness": -1.8, "calm": -1.8, "relaxed": -1.8,
    "peaceful": -1.8, "great": -1.2, "fine": -0.6, "good": -0.6,
    "positive": -1.2, "motivated": -1.6, "energetic": -1.2, "rested": -1.2,
    "balanced": -1.4, "focused": -1.0, "confident": -1.4, "content": -1.4,
    "grateful": -1.6, "excited": -1.0, "comfortable": -1.0, "stable": -1.4,
    "optimistic": -1.6, "cheerful": -1.6, "enjoying": -1.2, "improving": -1.0,
}

_sia = SentimentIntensityAnalyzer()


def analyze_text_stress(text: str) -> Dict:
    """
    Returns stress score 0–100 for a single text answer.
    Combines VADER compound score with custom keyword lexicon.
    """
    if not text or text.strip() in ("", "(No response)"):
        return {
            "stress_score": 50.0,
            "vader_compound": 0.0,
            "keyword_hits": [],
            "explanation": "No answer provided — neutral score assumed.",
        }

    # VADER sentiment (compound: -1 to +1)
    vader = _sia.polarity_scores(text)
    # Convert to stress: very negative → high stress
    # compound=-1 → stress=100, compound=+1 → stress=0
    vader_stress = (-vader["compound"] + 1.0) / 2.0 * 100.0

    # Keyword scoring (baseline 50)
    keyword_score = 50.0
    keyword_hits = []
    for word in text.lower().split():
        clean = word.strip(".,!?;:'\"()-")
        if clean in STRESS_LEXICON:
            keyword_score += STRESS_LEXICON[clean] * 5.0
            keyword_hits.append(clean)
    keyword_score = max(0.0, min(100.0, keyword_score))

    # Combined: 60% VADER, 40% keyword
    stress_score = vader_stress * 0.60 + keyword_score * 0.40

    explanation = ""
    if keyword_hits:
        explanation = f"Detected stress-related terms: {', '.join(set(keyword_hits))}."

    return {
        "stress_score": round(stress_score, 2),
        "vader_compound": round(vader["compound"], 4),
        "keyword_hits": list(set(keyword_hits)),
        "explanation": explanation,
    }


def analyze_all_responses(responses: List[Dict]) -> Dict:
    """
    Aggregates stress scores across all Q&A pairs.
    Returns avg text_stress_score + per-answer detail.
    """
    if not responses:
        return {"text_stress_score": 50.0, "per_answer": [], "explanation": ""}

    per_answer = []
    scores = []
    for resp in responses:
        result = analyze_text_stress(resp.get("answer", ""))
        per_answer.append({
            "question": resp.get("question", ""),
            "answer": resp.get("answer", ""),
            **result,
        })
        scores.append(result["stress_score"])

    avg = sum(scores) / len(scores)

    # Collect most frequent keyword hits for overall explanation
    all_hits = [h for pa in per_answer for h in pa.get("keyword_hits", [])]
    freq = {}
    for h in all_hits:
        freq[h] = freq.get(h, 0) + 1
    top = sorted(freq, key=freq.get, reverse=True)[:5]
    explanation = f"Most frequent stress-related terms across answers: {', '.join(top)}." if top else ""

    return {
        "text_stress_score": round(avg, 2),
        "per_answer": per_answer,
        "explanation": explanation,
    }
