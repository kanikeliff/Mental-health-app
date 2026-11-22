from app.firebase_admin_box import firestore_bag


def get_firestore():
    """Return the configured Firestore client.

    Tests should override this dependency with a fake client.
    """
    return firestore_bag()
