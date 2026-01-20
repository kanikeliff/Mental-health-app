import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException
from app.services.firebase_service import firestore_db, verify_firebase_bearer
from app.models.assessment import AssessmentIn

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("")
async def save_assessment(payload: AssessmentIn, authorization: str = Header(default="")):
    """
    I keep assessments very flexible today.
    iOS can either compute score locally or send it here.
    """

    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    db = firestore_db()
    a_id = "as_" + str(uuid.uuid4())

    db.collection("users").document(uid).collection("assessments").document(a_id).set({
        "id": a_id,
        "timestamp": datetime.now(timezone.utc),
        "kind": payload.kind,
        "answers": payload.answers,
        "score": payload.score
    })

    return {"assessmentId": a_id, "saved": True}
