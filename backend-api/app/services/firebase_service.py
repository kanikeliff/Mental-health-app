# backend-api/app/services/firebase_service.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

# I make Firebase optional so the service can boot on Render even if credentials are missing.
# If DEV_AUTH_BYPASS=true, I skip verification and DB entirely.

firestore_db = None  # I always export this symbol so imports never crash.


def env_timezone() -> str:
    # I keep timezone configurable so timestamps stay consistent.
    return os.getenv("APP_TIMEZONE", "Europe/Istanbul")


def verify_firebase_bearer(auth_header: Optional[str]) -> Dict[str, Any]:
    """
    I verify Authorization: Bearer <token>.
    - In dev bypass, I return a fake user payload so endpoints can run.
    - Otherwise, I try to verify using firebase_admin if configured.
    """
    if os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true":
        return {"uid": "dev-user", "email": "dev@local", "provider": "bypass"}

    token = _extract_bearer_token(auth_header)
    if not token:
        raise ValueError("Missing Bearer token")

    # I import firebase lazily so import-time never crashes.
    import firebase_admin
    from firebase_admin import auth

    if not firebase_admin._apps:
        # I expect GOOGLE_APPLICATION_CREDENTIALS or other Firebase default creds in prod.
        firebase_admin.initialize_app()

    decoded = auth.verify_id_token(token)
    # I normalize the payload a bit for my app.
    return {
        "uid": decoded.get("uid") or decoded.get("sub"),
        "email": decoded.get("email"),
        "provider": "firebase",
        "raw": decoded,
    }


def verify_firebase_token(auth_header: Optional[str]) -> Dict[str, Any]:
    # Some files used this old name, so I keep it as an alias.
    return verify_firebase_bearer(auth_header)


def init_firestore_if_possible() -> None:
    """
    I try to initialize Firestore and set firestore_db.
    I never crash the app if Firestore isn't available.
    """
    global firestore_db

    if os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true":
        firestore_db = None
        return

    try:
        import firebase_admin
        from firebase_admin import firestore

        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        firestore_db = firestore.client()
    except Exception:
        # I keep firestore_db as None if Firestore is not configured.
        firestore_db = None


def _extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2:
        return None
    scheme, token = parts[0].lower(), parts[1].strip()
    if scheme != "bearer" or not token:
        return None
    return token
