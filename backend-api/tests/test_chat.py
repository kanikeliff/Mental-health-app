from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api import chat
from app.main import app


def test_chat_passes_authorization_header_and_uid(monkeypatch):
    verify = Mock(return_value={"uid": "firebase-user"})
    reply = Mock(return_value={"assistantText": "How can I help?", "metadata": {}})
    monkeypatch.setattr(chat, "verify_firebase_bearer", verify)
    monkeypatch.setattr(chat, "generate_chat_reply", reply)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"userText": "I feel stressed today"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["assistantText"] == "How can I help?"
    verify.assert_called_once_with("Bearer test-token")
    reply.assert_called_once()
    assert reply.call_args.kwargs["user_id"] == "firebase-user"


def test_chat_rejects_invalid_token_before_calling_ai(monkeypatch):
    verify = Mock(side_effect=ValueError("Invalid token"))
    reply = Mock()
    monkeypatch.setattr(chat, "verify_firebase_bearer", verify)
    monkeypatch.setattr(chat, "generate_chat_reply", reply)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"userText": "I feel stressed today"},
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401, response.text
    reply.assert_not_called()
