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
    
    # --- QUICK PATCH: make imports stable for Render ---
    # I expose the symbols that the routers import.
    # I also avoid crashing at import-time if Firebase is not configured.
    
    import os
    
    def env_timezone() -> str:
        # I keep timezone configurable for consistent timestamps.
        return os.getenv("APP_TIMEZONE", "Europe/Istanbul")
    
    def verify_firebase_bearer(auth_header: str | None):
        # I allow dev bypass so Render can boot without Firebase credentials.
        if os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true":
            return {"uid": "dev-user", "email": "dev@local", "provider": "bypass"}
    
        # If the project already has a real verifier function, I try to use it.
        # Otherwise I fail clearly.
        if "verify_firebase_token" in globals():
            return globals()["verify_firebase_token"](auth_header)
    
        raise RuntimeError("Firebase verification is not configured (DEV_AUTH_BYPASS is false).")
    
    # Some files import verify_firebase_token by name, so I keep an alias.
    def verify_firebase_token(auth_header: str | None):
        return verify_firebase_bearer(auth_header)
    
    # I must define firestore_db as a module-level symbol.
    # If DEV_AUTH_BYPASS is true (or Firestore isn't configured), I set it to None.
    try:
        if os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true":
            firestore_db = None
        else:
            # If your file already creates a firestore client somewhere, reuse it.
            # Common names: db, firestore_client, client
            if "firestore_db" in globals():
                firestore_db = globals()["firestore_db"]
            elif "db" in globals():
                firestore_db = globals()["db"]
            elif "firestore_client" in globals():
                firestore_db = globals()["firestore_client"]
            else:
                # Last resort: try to create client if firebase_admin is present & initialized.
                import firebase_admin
                from firebase_admin import firestore
    
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
    
                firestore_db = firestore.client()
    except Exception:
        firestore_db = None
    # --- END QUICK PATCH ---
