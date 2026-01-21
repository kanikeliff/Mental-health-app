from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import auth as fb_auth
from firebase_admin import credentials, firestore
from pydantic_settings import BaseSettings


# I keep config inside this file to avoid scattering env reads everywhere.
# Render will use env vars, local can use .env.
class _Env(BaseSettings):
    FIREBASE_PROJECT_ID: str = ""
    # On Render, this MUST be the full JSON string of the service account.
    # Locally, I may also set it to a file path for convenience.
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""
    DEFAULT_TZ: str = "Europe/Istanbul"

    # DEV bypass is ONLY for local/testing (or temporary staging).
    DEV_BYPASS_AUTH: str = ""
    DEV_BYPASS_UID: str = "dev-user"

    class Config:
        env_file = ".env"
        extra = "ignore"


_env = _Env()
_db_cache = None


def _truthy(v: str) -> bool:
    return (v or "").strip().lower() in ("1", "true", "yes", "y", "on")


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
        sa_value = (_env.FIREBASE_SERVICE_ACCOUNT_JSON or "").strip()
        if not sa_value:
            raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT_JSON env var")

        # If it looks like a path, read JSON from file. Otherwise treat it as raw JSON string.
        if sa_value.endswith(".json") and os.path.exists(sa_value):
            with open(sa_value, "r", encoding="utf-8") as f:
                sa: Dict[str, Any] = json.load(f)
        else:
            sa = json.loads(sa_value)

        cred = credentials.Certificate(sa)

        # I set projectId explicitly so I don't accidentally hit the wrong project.
        project_id = (_env.FIREBASE_PROJECT_ID or sa.get("project_id") or "").strip()
        if not project_id:
            raise RuntimeError("Missing FIREBASE_PROJECT_ID (and could not infer from service account)")

        firebase_admin.initialize_app(cred, {"projectId": project_id})

    _db_cache = firestore.client()
    return _db_cache


def verify_firebase_bearer(auth_header: Optional[str]) -> str:
    """
    I verify Firebase ID tokens here.
    Important: I never trust uid coming from request body,
    only from a verified token.
    """
    # DEV bypass: I use this to test without Firebase on local / staging.
    if _truthy(os.getenv("DEV_BYPASS_AUTH", _env.DEV_BYPASS_AUTH)):
        return os.getenv("DEV_BYPASS_UID", _env.DEV_BYPASS_UID) or "dev-user"

    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing Bearer token")

    raw_token = auth_header.split(" ", 1)[1].strip()
    if not raw_token:
        raise ValueError("Empty token")

    # IMPORTANT: firebase_admin throws its own exception types.
    # I convert them to ValueError so my API layer can consistently return 401.
    try:
        decoded = fb_auth.verify_id_token(raw_token)
    except Exception as e:
        raise ValueError("Invalid Firebase token") from e

    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Token missing uid")
    return uid


def env_timezone() -> str:
    return _env.DEFAULT_TZ
