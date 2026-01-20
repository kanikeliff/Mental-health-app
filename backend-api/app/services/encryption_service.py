import base64


def pack_private_report(text_blob: str) -> str:
    """
    I did NOT implement real encryption today because it would require key management.
    For demo, I just base64-encode the report so payload is 'transport-friendly'.

    Later:
    - We can use proper encryption (AES/GCM) with a user-specific key.
    - Or iOS can encrypt locally (even better).
    """
    raw = (text_blob or "").encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")
