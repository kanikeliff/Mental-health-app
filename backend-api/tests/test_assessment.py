from unittest.mock import MagicMock

import pytest

from app.api import assessments
from app.main import app
from app.services.firestore_provider import get_firestore


@pytest.fixture
def assessment_db(monkeypatch):
    db = MagicMock()
    monkeypatch.setitem(app.dependency_overrides, get_firestore, lambda: db)
    monkeypatch.setattr(
        assessments, "verify_firebase_bearer", lambda authorization: {"uid": "u1"}
    )
    return db
def test_get_phq9_questions(client):
    r = client.get("/assessments/questions/phq9")
    assert r.status_code == 200
    j = r.json()
    assert j["name"] == "phq9"
    assert len(j["questions"]) == 9

def test_submit_phq9_missing_answers(client, assessment_db):
    r = client.post("/assessments/submit/phq9", headers={"Authorization": "Bearer test-token"}, json={
        "answers": { "phq9_q1": 1 }  # incomplete
    })
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is False
    assert "Missing answers" in " ".join(j["errors"])
    assessment_db.collection.assert_not_called()

def test_submit_phq9_scoring_and_safety(client, assessment_db):
    # all 9 answered
    answers = {f"phq9_q{i}": 0 for i in range(1, 10)}
    answers["phq9_q9"] = 1  # triggers safety flag
    r = client.post("/assessments/submit/phq9", headers={"Authorization": "Bearer test-token"}, json={"answers": answers})
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["result"]["total_score"] == 1
    assert j["result"]["safety_flag"] is True
    user = assessment_db.collection.return_value.document
    user.assert_called_once_with("u1")
    collection = user.return_value.collection
    collection.assert_called_once_with("assessments")
    document = collection.return_value.document
    document.assert_called_once_with(j["assessmentId"])
    write = document.return_value.set
    write.assert_called_once()
    saved = write.call_args.args[0]
    assert saved["answers"] == answers
    assert saved["result"] == j["result"]

def test_submit_who5(client, assessment_db):
    answers = {f"who5_q{i}": 5 for i in range(1, 6)}
    r = client.post("/assessments/submit/who5", headers={"Authorization": "Bearer test-token"}, json={"answers": answers})
    j = r.json()
    assert j["ok"] is True
    assert j["result"]["total_score"] == 25
    assert j["result"]["score_0_100"] == 100
