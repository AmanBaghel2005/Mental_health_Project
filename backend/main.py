from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from auth import otp_store, generate_otp, send_otp_email, create_access_token, verify_token
from config import settings
from questionnaire_data import QUESTIONNAIRE
from questionnaire_scoring import compute_questionnaire_score
from blink_analysis import compute_blink_score
from emotion_analysis import compute_emotion_score
from stress_scoring import compute_final_stress_score

app = FastAPI(title="BehavioralSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth models ───────────────────────────────────────────────────────────────
class EmailRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

# ── Session model ─────────────────────────────────────────────────────────────
class VisualData(BaseModel):
    blink_count: int = 0
    blink_rate_bpm: float = 0.0
    session_duration_s: float = 0.0
    emotion_distribution: Optional[Dict[str, float]] = None
    dominant_emotion: Optional[str] = None

class SessionData(BaseModel):
    age_group: str
    visual_data: VisualData
    answers: List[int]  # Likert scale values (1-5), one per question

# ── Auth endpoints ────────────────────────────────────────────────────────────
@app.post("/auth/send-otp")
async def send_otp(request: EmailRequest):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    otp_store[request.email] = {"otp": otp, "expiry": expiry, "retries": 0}

    print(f"\n{'='*50}")
    print(f"  OTP for {request.email}: {otp}")
    print(f"  Expires at: {expiry.strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")

    email_sent = send_otp_email(request.email, otp)

    if email_sent:
        return {"message": "OTP sent to your email", "email_sent": True}
    else:
        return {
            "message": "OTP generated (email delivery failed — check console)",
            "debug_otp": otp,
            "email_sent": False,
        }

@app.post("/auth/verify-otp")
async def verify_otp(request: VerifyRequest):
    if request.email not in otp_store:
        raise HTTPException(status_code=400, detail="OTP not requested for this email")
    stored = otp_store[request.email]
    if datetime.utcnow() > stored["expiry"]:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="OTP expired")
    if stored["retries"] >= settings.MAX_OTP_RETRIES:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="Too many retries")
    if stored["otp"] != request.otp:
        stored["retries"] += 1
        raise HTTPException(status_code=400, detail="Invalid OTP")
    access_token = create_access_token(data={"sub": request.email})
    del otp_store[request.email]
    return {"access_token": access_token, "token_type": "bearer"}

# ── Questionnaire endpoints ──────────────────────────────────────────────────
@app.get("/questionnaire/questions")
async def get_questions(age_group: str):
    """Return the question list for the given age group."""
    if age_group not in QUESTIONNAIRE:
        raise HTTPException(status_code=400, detail=f"Invalid age group: {age_group}")
    return {"questions": QUESTIONNAIRE[age_group], "count": len(QUESTIONNAIRE[age_group])}

# ── Session processing ────────────────────────────────────────────────────────
@app.post("/session/process")
async def process_session(
    data: SessionData,
    current_user: str = Depends(verify_token),
):
    vd = data.visual_data

    # 1. Questionnaire scoring (Likert scale)
    q_result = compute_questionnaire_score(data.age_group, data.answers)
    if "error" in q_result:
        raise HTTPException(status_code=400, detail=q_result["error"])
    q_stress = q_result["questionnaire_score"]

    # 2. Blink anomaly score (from real MediaPipe data)
    blink_result = compute_blink_score(
        blink_count=vd.blink_count,
        session_duration_s=vd.session_duration_s,
        blink_rate_bpm=vd.blink_rate_bpm if vd.blink_rate_bpm > 0 else None,
    )

    # 3. Emotion stress score (from real face-api.js data)
    emotion_result = compute_emotion_score(vd.emotion_distribution)

    # 4. Weighted final score (40% questionnaire, 30% emotion, 30% blink)
    final = compute_final_stress_score(
        questionnaire_score=q_stress,
        emotion_score=emotion_result["emotion_score"],
        blink_score=blink_result["blink_score"],
        questionnaire_explanation=f"Psychological stress: {q_stress:.0f}% ({q_result['stress_level']})",
        emotion_explanation=emotion_result.get("explanation", ""),
        blink_explanation=blink_result.get("explanation", ""),
    )

    return {
        **final,
        "questionnaire": {
            "score": q_result["questionnaire_score"],
            "level": q_result["stress_level"],
            "total": q_result["total_score"],
            "max": q_result["max_possible"],
            "categories": q_result["category_breakdown"],
        },
        "visual_summary": {
            "avg_blink_rate": blink_result["blink_rate_bpm"],
            "blink_status": blink_result["blink_status"],
            "dominant_emotion": emotion_result["dominant_emotion"],
            "emotion_distribution": emotion_result["emotion_distribution"],
            "emotion_stress_score": emotion_result["emotion_score"],
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
