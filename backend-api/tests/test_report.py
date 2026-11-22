from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from app.api import report
from app.main import app
from app.services.firestore_provider import get_firestore


def test_report_creation(client, monkeypatch):
    db = Mock()
    monkeypatch.setitem(app.dependency_overrides, get_firestore, lambda: db)
    monkeypatch.setattr(
        report, "verify_firebase_bearer", lambda authorization: {"uid": "u1"}
    )
    pack = Mock(return_value="packed-report")
    monkeypatch.setattr(report, "pack_private_report", pack)

    users = db.collection.return_value
    user = users.document.return_value
    moods = Mock()
    reports = Mock()
    user.collection.side_effect = {"moods": moods, "reports": reports}.__getitem__

    now = datetime.now(timezone.utc)
    moods.stream.return_value = [
        Mock(to_dict=Mock(return_value={
            "timestamp": now - timedelta(days=1), "moodScore": 3,
        })),
        Mock(to_dict=Mock(return_value={
            "timestamp": now - timedelta(days=10), "moodScore": 5,
        })),
        Mock(to_dict=Mock(return_value={
            "timestamp": now - timedelta(days=30), "moodScore": 1,
        })),
    ]

    response = client.post(
        "/report",
        params={"weeks": 2},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["reportId"].startswith("rep_")
    assert "- Entries: 2\n" in data["content"]
    assert "- Avg mood: 4.0\n" in data["content"]
    assert data["packed"] == "packed-report"
    pack.assert_called_once_with(data["content"])

    db.collection.assert_called_with("users")
    users.document.assert_called_with("u1")
    reports.document.assert_called_once_with(data["reportId"])
    write = reports.document.return_value.set
    write.assert_called_once()
    saved = write.call_args.args[0]
    assert saved["id"] == data["reportId"]
    assert saved["weeks"] == 2
    assert saved["content"] == data["content"]
