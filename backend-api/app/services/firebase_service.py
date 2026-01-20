from __future__ import annotations

import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import auth as fb_auth
from firebase_admin import credentials, firestore
from pydantic_settings import BaseSettings


# I keep config inside this file to avoid scattering env reads everywhere.
class _Env(BaseSettings):
    FIREBASE_PROJECT_ID: str
    FIREBASE_SERVICE_ACCOUNT_JSON: str
    DEFAULT_TZ: str = "Europe/Istanbul"

    class Config:
        env_file = ".env"
        extra = "ignore"


_env = _Env()

_db_cache: Optional[firestore.Client] = None


def _load_service_account_cred() -> credentials.Certificate:
    """
    FIREBASE_SERVICE_ACCOUNT_JSON can be either:
    - a JSON string (Render-friendly), OR
    - a file path like ./secrets/firebase-admin.json (Codespaces-friendly)
    """
    raw = (_env.FIREBASE_SERVICE_ACCOUNT_JSON or "").strip()
    if not raw:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON is empty")

    # 1) If it looks like JSON, parse it
    if raw.startswith("{"):
        data = json.loads(raw)
        return credentials.Certificate(data)

    # 2) Otherwise treat as file path
    path = raw
    if not os.path.isabs(path):
        # Make relative paths relative to backend-api root (where .env lives)
        # In Codespaces you usually run from backend-api, so this is fine.
        path = os.path.join(os.getcwd(), path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Service account file not found: {path}")

    return credentials.Certificate(path)


def firestore_db():
    """
    I did this function because every endpoint needs DB access.
    I also cache it so we don't re-init Firebase on each request.
    """
    global _db_cache

    if _db_cache is not None:
        return _db_cache

    # Firebase Admin should init once per process.
    if not firebase_admin._apps:
        cred = _load_service_account_cred()
        firebase_admin.initialize_app(cred, {"projectId": _env.FIREBASE_PROJECT_ID})

    _db_cache = firestore.client()
    return _db_cache


def verify_firebase_bearer(auth_header: str) -> str:
    """
    I verify Firebase ID tokens here.
    Important: I never trust uid coming from request body,
    only from a verified token.
    """

    # ✅ DEV BYPASS (local testing)
    if os.getenv("DEV_BYPASS_AUTH", "").lower() in ("1", "true", "yes"):
        return os.getenv("DEV_BYPASS_UID", "dev-user")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing Bearer token")

    raw_token = auth_header.split(" ", 1)[1].strip()
    if not raw_token:
        raise ValueError("Empty token")

    decoded = fb_auth.verify_id_token(raw_token)
    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Token missing uid")
    return uid


def env_timezone() -> str:
    return _env.DEFAULT_TZ
