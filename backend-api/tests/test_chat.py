import pytest
def test_chat_endpoint(client):
    payload = {
        "message": "I feel stressed today"
    }

    r = client.post(
        "/chat",
        json=payload,
        headers={"Authorization": "Bearer dev"}
    )

    assert r.status_code == 200

    j = r.json()
    assert "reply" in j
    assert isinstance(j["reply"], str)
