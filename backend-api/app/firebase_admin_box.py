import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore


def _my_key_path() -> str:
    # I keep the key path in env so local + Render can be configured differently
    where_is_my_key = (os.getenv("FIREBASE_ADMIN_KEY_PATH") or "").strip()

    if not where_is_my_key:
        raise RuntimeError(
            "FIREBASE_ADMIN_KEY_PATH is missing. "
            "Example: secrets/firebase-admin.json"
        )

    if not os.path.exists(where_is_my_key):
        raise RuntimeError(f"Firebase admin json not found at: {where_is_my_key}")

    return where_is_my_key


@lru_cache(maxsize=1)
def firestore_bag():
    # I cache this so I don't re-init Firebase on every request like a maniac
    if not firebase_admin._apps:
        key_path = _my_key_path()
        cred = credentials.Certificate(key_path)

        # I name the app for clarity in logs if we ever add more services later
        firebase_admin.initialize_app(cred, name="nuvio-backend-admin")

    return firestore.client()
