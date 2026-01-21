# backend-api/app/services/firebase_service.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

try:
    import firebase_admin
    from firebase_admin import auth
except Exception:
    firebase_admin = None
    auth = None


def verify_firebase_token(auth_header: Optional[str]) -> Dict[str, Any]:
    # I accept "Authorization: Bearer <token>" format from the client.
    # If DEV_AUTH_BYPASS=true, I skip real Firebase verification for quick testing.
    dev_bypass = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"

    if dev_bypass:
        # I return a fake but stable payload so downstream code works the same way.
        return {"uid": "dev-user", "email": "dev@local", "provider": "bypass"}

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )

    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
        )

    if auth is None:
        # I fail loudly if Firebase isn't available in prod mode.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase SDK not available",
        )

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        )
