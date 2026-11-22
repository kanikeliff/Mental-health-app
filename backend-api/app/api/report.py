import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Header, HTTPException, Depends
from app.services.firestore_provider import get_firestore

from app.services.firebase_service import verify_firebase_bearer
from app.services.encryption_service import pack_private_report

router = APIRouter(prefix="/report", tags=["report"])


@router.post("")
async def make_report(authorization: str = Header(default=""), weeks: int = 1, db = Depends(get_firestore)):
    """
    For today:
    - I generate a simple text report.
    - I store it in Firestore under users/{uid}/reports/{reportId}.
    """

    try:
        uid = verify_firebase_bearer(authorization)["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    if not 1 <= weeks <= 52:
        raise HTTPException(
            status_code=422,
            detail="weeks must be between 1 and 52",
        )

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(weeks=weeks)

    moods = db.collection("users").document(uid).collection("moods").stream()

    scores = []
    for m in moods:
        d = m.to_dict() or {}

        timestamp = d.get("timestamp")
        if not isinstance(timestamp, datetime):
            continue

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        timestamp = timestamp.astimezone(timezone.utc)

        if not cutoff <= timestamp <= now:
            continue

        score = d.get("moodScore")
        if isinstance(score, bool):
            continue

        try:
            score = int(score)
        except (TypeError, ValueError, OverflowError):
            continue

        if not 1 <= score <= 5:
            continue

        scores.append(score)

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
