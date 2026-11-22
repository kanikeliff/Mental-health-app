from unittest.mock import Mock

import pytest
from firebase_admin import auth

from app import firebase_admin_box as box
from app.services.firebase_service import verify_firebase_bearer


@pytest.mark.parametrize("key_path", [None, "/local/firebase-admin.json"])
def test_firestore_and_auth_share_firebase_app(monkeypatch, key_path):
    monkeypatch.delenv("DEV_AUTH_BYPASS", raising=False)
    monkeypatch.delenv("FIREBASE_ADMIN_KEY_PATH", raising=False)
    credential = None
    if key_path is not None:
        monkeypatch.setenv("FIREBASE_ADMIN_KEY_PATH", key_path)
        credential = object()

    app = object()
    db = object()
    initialize = Mock(return_value=app)
    certificate = Mock(return_value=credential)
    firestore_client = Mock(return_value=db)
    verify_token = Mock(return_value={"uid": "test-user"})

    monkeypatch.setattr(box.firebase_admin, "get_app", Mock(side_effect=[ValueError(), app]))
    monkeypatch.setattr(box.firebase_admin, "initialize_app", initialize)
    monkeypatch.setattr(box.credentials, "Certificate", certificate)
    monkeypatch.setattr(box.firestore, "client", firestore_client)
    monkeypatch.setattr(auth, "verify_id_token", verify_token)

    box.firestore_bag.cache_clear()
    try:
        assert box.firestore_bag() is db
        assert verify_firebase_bearer("Bearer test-token")["uid"] == "test-user"
    finally:
        box.firestore_bag.cache_clear()

    initialize.assert_called_once_with(credential)
    if key_path is None:
        certificate.assert_not_called()
    else:
        certificate.assert_called_once_with(key_path)
    firestore_client.assert_called_once_with(app=app)
    verify_token.assert_called_once_with("test-token", app=app)
