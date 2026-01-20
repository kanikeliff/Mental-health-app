import json
import firebase_admin
from firebase_admin import credentials, firestore, auth as fb_auth
from pydantic_settings import BaseSettings
import os

def verify_firebase_bearer(authorization: str) -> str:
    if os.getenv("DEV_BYPASS_AUTH", "").lower() in ("1", "true", "yes"):
        return "dev-user"
    # normal verify devam...


# I keep config inside this file to avoid scattering env reads everywhere.
# If you already have a config file somewhere else, we can move it later.
class _Env(BaseSettings):
    FIREBASE_PROJECT_ID: str
    FIREBASE_SERVICE_ACCOUNT_JSON: str
    DEFAULT_TZ: str = "Europe/Istanbul"

    class Config:
        env_file = ".env"
        extra = "ignore"


_env = _Env()

_db_cache = None


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
        # I store service account JSON in env var (Render-friendly).
        sa = json.loads(_env.FIREBASE_SERVICE_ACCOUNT_JSON)
        cred = credentials.Certificate(sa)

        # I set projectId explicitly so I don't accidentally hit the wrong project.
        firebase_admin.initialize_app(cred, {"projectId": _env.FIREBASE_PROJECT_ID})

    _db_cache = firestore.client()
    return _db_cache


def verify_firebase_bearer(auth_header: str) -> str:
    """
    I verify Firebase ID tokens here.
    Important: I never trust uid coming from request body,
    only from a verified token.
    """
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
    # I expose this so other modules can reuse the timezone config.
    return _env.DEFAULT_TZ
