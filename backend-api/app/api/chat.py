import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from app.services.firebase_service import firestore_db, verify_firebase_bearer
from app.services.ai_service import generate_chat_reply
from app.models.chat import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatOut)
async def chat(payload: ChatIn, authorization: str = Header(default="")):
    """
    iOS sends Firebase ID token in Authorization header.
    I validate it and use uid for scoping.
    """

    # 1) Auth
    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        # I keep it simple: 401 if token invalid.
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    # 2) Firestore collection path matches your iOS plan:
    # users/{uid}/chat/{messageId}
    db = firestore_db()
    chat_box = db.collection("users").document(uid).collection("chat")

    # 3) I generate stable-ish ids
    user_msg_id = payload.clientMessageId or str(uuid.uuid4())

    # 4) Save user message first (I do this so we never lose user input)
    chat_box.document(user_msg_id).set({
        "id": user_msg_id,
        "timestamp": datetime.now(timezone.utc),
        "role": "user",
        "content": payload.userText.strip(),
        "metadata": {}
    })

    result = generate_chat_reply(
        user_id=uid,
        user_text=payload.userText,
    )

    assistant_text = result["assistant_reply"]
    meta = {
        "safety": result.get("safety"),
        "tags": result.get("tags", []),
        "tone": result.get("tone"),
        "follow_up_questions": result.get("follow_up_questions", []),
        "debug": result.get("debug"),
    }

    # 6) Save assistant message
    bot_id = str(uuid.uuid4())
    chat_box.document(bot_id).set({
        "id": bot_id,
        "timestamp": datetime.now(timezone.utc),
        "role": "assistant",
        "content": assistant_text,
        "metadata": meta
    })

    return ChatOut(assistantText=assistant_text, metadata=meta)
