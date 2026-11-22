from datetime import datetime, timezone
from unittest.mock import Mock

from app.api import mood
from app.main import app
from app.services.firestore_provider import get_firestore


def test_mood_weekly(client, monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            fixed = cls(2026, 11, 18, 12, tzinfo=timezone.utc)
            return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)

    monkeypatch.setattr(mood, "datetime", FixedDatetime)
    monkeypatch.setattr(mood, "env_timezone", lambda: "UTC")
    monkeypatch.setattr(
        mood, "verify_firebase_bearer", lambda authorization: {"uid": "u1"}
    )

    db = Mock()
    monkeypatch.setitem(app.dependency_overrides, get_firestore, lambda: db)
    users = db.collection.return_value
    user = users.document.return_value
    moods = user.collection.return_value
    moods.stream.return_value = [
        Mock(to_dict=Mock(return_value={
            "timestamp": datetime(2026, 11, 18, 10, tzinfo=timezone.utc),
            "moodScore": 3,
        })),
        Mock(to_dict=Mock(return_value={
            "timestamp": datetime(2026, 11, 18, 11, tzinfo=timezone.utc),
            "moodScore": 5,
        })),
    ]

    response = client.get(
        "/mood/weekly", headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json()["mood"] == {
        "count": 2,
        "avg": 4.0,
        "min": 3,
        "max": 5,
        "points": [{"date": "2026-11-18", "avg": 4.0}],
    }
    db.collection.assert_called_once_with("users")
    users.document.assert_called_once_with("u1")
    user.collection.assert_called_once_with("moods")
