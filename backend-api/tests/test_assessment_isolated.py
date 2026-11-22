from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import assessments


@pytest.fixture
def isolated_client(monkeypatch):
    fake_db = MagicMock()

    monkeypatch.setattr(
        assessments,
        "verify_firebase_bearer",
        lambda authorization: {"uid": "test-user"},
    )

    from app.services.firestore_provider import get_firestore

    app.dependency_overrides[get_firestore] = lambda: fake_db

    try:
        with TestClient(app) as client:
            yield client, fake_db
    finally:
        app.dependency_overrides.pop(get_firestore, None)


def test_missing_answers_without_firestore(isolated_client):
    client, fake_db = isolated_client

    response = client.post(
        "/assessments/submit/phq9",
        json={"answers": {"phq9_q1": 1}},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["ok"] is False
    fake_db.collection.assert_not_called()


def test_valid_phq9_with_mock_firestore(isolated_client):
    client, fake_db = isolated_client

    answers = {
        f"phq9_q{i}": 0
        for i in range(1, 10)
    }
    answers["phq9_q9"] = 1

    response = client.post(
        "/assessments/submit/phq9",
        json={"answers": answers},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["result"]["total_score"] == 1
    assert data["result"]["safety_flag"] is True

    fake_db.collection.assert_called_with("users")

    user_document = fake_db.collection.return_value.document
    user_document.assert_called_once_with("test-user")
