import os
from functools import lru_cache
from threading import Lock

import firebase_admin
from firebase_admin import credentials, firestore


_firebase_app_lock = Lock()


def get_firebase_app() -> firebase_admin.App:
    """Return the Firebase app shared by token verification and Firestore."""
    with _firebase_app_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            key_path = (os.getenv("FIREBASE_ADMIN_KEY_PATH") or "").strip()
            credential = credentials.Certificate(key_path) if key_path else None
            return firebase_admin.initialize_app(credential)


@lru_cache(maxsize=1)
def firestore_bag():
    return firestore.client(app=get_firebase_app())
