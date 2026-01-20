from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Header, HTTPException

from app.services.firebase_service import firestore_db, verify_firebase_bearer, env_timezone

router = APIRouter(prefix="/mood", tags=["mood"])


@router.get("/weekly")
async def weekly_insights(authorization: str = Header(default=""), weeks: int = 1):
    """
    I compute weekly mood stats from Firestore moods.
    Path: users/{uid}/moods/{moodDocId}
    """

    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    tz_name = env_timezone()
    tz = ZoneInfo(tz_name)

    now_local = datetime.now(timezone.utc).astimezone(tz)
    start = (now_local - timedelta(days=now_local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start = start - timedelta(days=7 * (weeks - 1))
    end = start + timedelta(days=7 * weeks)

    db = firestore_db()
    moods = db.collection("users").document(uid).collection("moods").stream()

    scores = []
    per_day = {}

    for m in moods:
        d = m.to_dict() or {}
        ts = d.get("timestamp")
        score = d.get("moodScore")
        if not ts or score is None:
            continue

        ts_local = ts.replace(tzinfo=timezone.utc).astimezone(tz)
        if not (start <= ts_local < end):
            continue

        try:
            s = int(score)
        except Exception:
            continue

        scores.append(s)
        key = ts_local.date().isoformat()
        per_day.setdefault(key, []).append(s)

    if not scores:
        return {
            "range": {"start": start.date().isoformat(), "end": end.date().isoformat(), "tz": tz_name},
            "mood": {"count": 0, "avg": None, "min": None, "max": None, "points": []},
        }

    points = []
    for day in sorted(per_day.keys()):
        a = sum(per_day[day]) / len(per_day[day])
        points.append({"date": day, "avg": round(a, 2)})

    return {
        "range": {"start": start.date().isoformat(), "end": end.date().isoformat(), "tz": tz_name},
        "mood": {
            "count": len(scores),
            "avg": round(sum(scores) / len(scores), 2),
            "min": min(scores),
            "max": max(scores),
            "points": points
        }
    }
