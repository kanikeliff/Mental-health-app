import pytest
def test_mood_endpoint(client):
    payload = {
        "score": 3,
        "note": "Feeling okay"
    }

    r = client.post(
        "/mood",
        json=payload,
        headers={"Authorization": "Bearer dev"}
    )

    assert r.status_code == 200

    j = r.json()
    assert j["saved"] is True
