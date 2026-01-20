import pytest
def test_get_phq9_questions(client):
    r = client.get("/assessments/questions/phq9")
    assert r.status_code == 200
    j = r.json()
    assert j["name"] == "phq9"
    assert len(j["questions"]) == 9

def test_submit_phq9_missing_answers(client):
    r = client.post("/assessments/submit/phq9", json={
        "user_id": "u1",
        "answers": { "phq9_q1": 1 }  # incomplete
    })
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is False
    assert "Missing answers" in " ".join(j["errors"])

def test_submit_phq9_scoring_and_safety(client):
    # all 9 answered
    answers = {f"phq9_q{i}": 0 for i in range(1, 10)}
    answers["phq9_q9"] = 1  # triggers safety flag
    r = client.post("/assessments/submit/phq9", json={"user_id": "u1", "answers": answers})
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["total_score"] == 1
    assert j["safety_flag"] is True

def test_submit_who5(client):
    answers = {f"who5_q{i}": 5 for i in range(1, 6)}
    r = client.post("/assessments/submit/who5", json={"user_id": "u1", "answers": answers})
    j = r.json()
    assert j["ok"] is True
    assert j["total_score"] == 25
    assert j["score_0_100"] == 100
