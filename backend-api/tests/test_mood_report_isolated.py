from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.firestore_provider import get_firestore
from app.api import mood, report


@pytest.fixture
def isolated_client(monkeypatch):
    fake_db = MagicMock()

    monkeypatch.setattr(
        mood,
        "verify_firebase_bearer",
        lambda authorization: {"uid": "test-user"},
    )
    monkeypatch.setattr(
        report,
        "verify_firebase_bearer",
        lambda authorization: {"uid": "test-user"},
    )

    # An empty Firestore query result.
    fake_db.collection.return_value.document.return_value \
        .collection.return_value.stream.return_value = iter([])

    app.dependency_overrides[get_firestore] = lambda: fake_db

    try:
        with TestClient(app) as client:
            yield client, fake_db
    finally:
        app.dependency_overrides.pop(get_firestore, None)


def test_weekly_mood_empty(isolated_client):
    client, fake_db = isolated_client

    response = client.get(
        "/mood/weekly",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["mood"]["count"] == 0
    assert data["mood"]["avg"] is None

    fake_db.collection.assert_called_with("users")
    fake_db.collection.return_value.document.assert_called_with(
        "test-user"
    )


def test_report_empty_moods(isolated_client):
    client, fake_db = isolated_client

    response = client.post(
        "/report",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["reportId"].startswith("rep_")
    assert "Entries: 0" in data["content"]

    fake_db.collection.assert_called_with("users")
    fake_db.collection.return_value.document.assert_called_with(
        "test-user"
    )

    report_collection = (
        fake_db.collection.return_value
        .document.return_value
        .collection
    )

    report_collection.assert_any_call("reports")


def test_weekly_mood_aggregation(isolated_client):
    client, fake_db = isolated_client

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    records = []
    for score in (3, 4, 5):
        record = MagicMock()
        record.to_dict.return_value = {
            "timestamp": now,
            "moodScore": score,
        }
        records.append(record)

    fake_db.collection.return_value.document.return_value \
        .collection.return_value.stream.return_value = iter(records)

    response = client.get(
        "/mood/weekly",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mood"]["count"] == 3
    assert data["mood"]["avg"] == 4.0
    assert data["mood"]["min"] == 3
    assert data["mood"]["max"] == 5


def test_weekly_mood_respects_timestamp_timezone(isolated_client, monkeypatch):
    from datetime import datetime, timezone, timedelta
    from zoneinfo import ZoneInfo
    from app.api import mood

    client, fake_db = isolated_client

    monkeypatch.setattr(mood, "env_timezone", lambda: "America/New_York")

    now_local = datetime.now(ZoneInfo("America/New_York"))
    monday = (now_local - timedelta(days=now_local.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # A timestamp representing Sunday 23:30 New York time.
    previous_sunday = monday - timedelta(minutes=30)

    record = MagicMock()
    record.to_dict.return_value = {
        "timestamp": previous_sunday.astimezone(timezone.utc),
        "moodScore": 5,
    }

    fake_db.collection.return_value.document.return_value \
        .collection.return_value.stream.return_value = iter([record])

    response = client.get(
        "/mood/weekly?weeks=1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["mood"]["count"] == 0


def test_report_excludes_old_mood_entries(isolated_client):
    from datetime import datetime, timezone, timedelta

    client, fake_db = isolated_client
    now = datetime.now(timezone.utc)

    records = []

    for timestamp, score in [
        (now - timedelta(days=1), 5),
        (now - timedelta(days=60), 1),
    ]:
        record = MagicMock()
        record.to_dict.return_value = {
            "timestamp": timestamp,
            "moodScore": score,
        }
        records.append(record)

    fake_db.collection.return_value.document.return_value \
        .collection.return_value.stream.return_value = iter(records)

    response = client.post(
        "/report?weeks=1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200

    content = response.json()["content"]

    assert "Entries: 1" in content
    assert "Avg mood: 5.0" in content


@pytest.mark.parametrize("weeks", [0, -1, 53])
def test_report_rejects_invalid_weeks(isolated_client, weeks):
    client, _ = isolated_client

    response = client.post(
        "/report",
        params={"weeks": weeks},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 422, response.text


@pytest.mark.parametrize("weeks, expected_count", [(1, 0), (2, 1), (52, 1)])
def test_report_uses_requested_window(isolated_client, weeks, expected_count):
    from datetime import timedelta

    client, fake_db = isolated_client
    record = MagicMock()
    record.to_dict.return_value = {
        "timestamp": datetime.now(timezone.utc) - timedelta(days=10),
        "moodScore": 4,
    }

    user_doc = fake_db.collection.return_value.document.return_value
    user_doc.collection.return_value.stream.return_value = iter([record])

    response = client.post(
        "/report",
        params={"weeks": weeks},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200, response.text
    assert f"- Entries: {expected_count}" in response.json()["content"].splitlines()
