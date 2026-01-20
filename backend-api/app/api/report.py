import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException

from app.services.firebase_service import firestore_db, verify_firebase_bearer
from app.services.encryption_service import pack_private_report

router = APIRouter(prefix="/report", tags=["report"])


@router.post("")
async def make_report(authorization: str = Header(default=""), weeks: int = 1):
    """
    For today:
    - I generate a simple text report.
    - I store it in Firestore under users/{uid}/reports/{reportId}.
    """

    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    db = firestore_db()
    moods = db.collection("users").document(uid).collection("moods").stream()

    scores = []
    for m in moods:
        d = m.to_dict() or {}
        if d.get("moodScore") is None:
            continue
        try:
            scores.append(int(d["moodScore"]))
        except Exception:
            pass

    avg = round(sum(scores) / len(scores), 2) if scores else None

    report_text = (
        f"Nuvio Weekly Report ({weeks} week(s))\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n"
        f"- Entries: {len(scores)}\n"
        f"- Avg mood: {avg}\n"
        f"- Min: {min(scores) if scores else None}\n"
        f"- Max: {max(scores) if scores else None}\n\n"
        "Disclaimer: informational only, not medical advice.\n"
    )

    report_id = "rep_" + str(uuid.uuid4())

    db.collection("users").document(uid).collection("reports").document(report_id).set({
        "id": report_id,
        "timestamp": datetime.now(timezone.utc),
        "weeks": weeks,
        "content": report_text
    })

    # I also give a packed version (base64) for easy transport.
    packed = pack_private_report(report_text)

    return {"reportId": report_id, "content": report_text, "packed": packed}
