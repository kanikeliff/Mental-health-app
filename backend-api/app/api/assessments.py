from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel

from app.services.assessment_service import load_assessment, score_assessment
from app.services.firebase_service import verify_firebase_bearer
from app.services.firestore_provider import get_firestore


router = APIRouter(prefix="/assessments", tags=["assessments"])


# =========================
# Pydantic Models
# =========================

class SubmitAssessmentIn(BaseModel):
    answers: Dict[str, int]
    session_id: Optional[str] = None


# =========================
# GET: Questions
# =========================

@router.get("/questions/{name}")
def get_questions(name: str) -> Dict[str, Any]:
    """
    Returns assessment metadata + questions.
    Used by iOS to render the assessment UI.
    """
    try:
        return load_assessment(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =========================
# POST: Submit Assessment
# =========================

@router.post("/submit/{name}")
async def submit_assessment(
    name: str,
    payload: SubmitAssessmentIn,
    authorization: str = Header(default=""),
    db = Depends(get_firestore),
):
    """
    Backend-authoritative assessment submit.

    Flow:
    1) Verify Firebase token
    2) Validate all questions answered
    3) Compute score & safety flags
    4) Save to Firestore
    """

    # 🔐 AUTH
    try:
        uid = verify_firebase_bearer(authorization)["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    # 🧮 VALIDATE + SCORE (deterministic)
    result = score_assessment(name, payload.answers)

    # ❌ Validation failed → iOS shows "Please answer all questions"
    if not result.get("ok"):
        return result

    # 💾 SAVE TO FIRESTORE
    assessment_id = "as_" + str(uuid.uuid4())

    db.collection("users") \
        .document(uid) \
        .collection("assessments") \
        .document(assessment_id) \
        .set({
            "id": assessment_id,
            "uid": uid,
            "kind": name,
            "answers": payload.answers,
            "result": result,
            "session_id": payload.session_id or "default",
            "timestamp": datetime.now(timezone.utc),
        })

    return {
        "ok": True,
        "assessmentId": assessment_id,
        "result": result,
    }