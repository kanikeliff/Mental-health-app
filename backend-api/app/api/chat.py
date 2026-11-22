from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter, Header, HTTPException
from app.models.schemas import ChatIn, ChatOut
from app.services.ai_service import generate_chat_reply
from app.services.firebase_service import verify_firebase_bearer


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
async def chat(
    payload: ChatIn,
    authorization: Optional[str] = Header(default=None),
) -> ChatOut:
    try:
        user_id = verify_firebase_bearer(authorization)["uid"]
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Firebase token") from exc

    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    # I call the AI service with the exact keyword names it expects.
    result: Dict[str, Any] = generate_chat_reply(
        payload.userText,
        user_id=user_id,
        conversation_id=payload.conversationId,
        history=payload.history,
    )

    return ChatOut(
        assistantText=result.get("assistantText", ""),
        metadata=result.get("metadata", {}),
    )
