from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Header, HTTPException
from app.models.schemas import ChatIn, ChatOut
from app.services.ai_service import generate_chat_reply
from app.services.firebase_service import verify_firebase_token


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
async def chat(
    payload: ChatIn,
    authorization: Optional[str] = Header(default=None),
) -> ChatOut:
    # I allow a dev bypass so I can hit /chat with curl without Firebase.
    dev_bypass = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"

    user_id = "dev-user"
    if not dev_bypass:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        token = authorization.split("Bearer ", 1)[1].strip()
        user_id = verify_firebase_token(token)

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
