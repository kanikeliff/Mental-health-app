# backend-api/app/api/chat.py
from __future__ import annotations

import logging
from fastapi import APIRouter, Header, HTTPException

from app.models.schemas import ChatIn, ChatOut
from app.services.ai_service import generate_chat_reply
from app.services.firebase_service import verify_firebase_bearer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn, authorization: str = Header(default="")) -> ChatOut:
    """
    I keep auth mandatory in production.
    If DEV_BYPASS_AUTH=true on Render, verify_firebase_bearer should return a dev uid.
    """
    try:
        uid = verify_firebase_bearer(authorization)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        result = generate_chat_reply(
            payload.userText,
            user_id=uid,
            conversation_id=payload.clientMessageId,
            history=None,
        )
        return ChatOut(**result)

    except Exception as e:
        # I log the full stack trace so I can debug Render without SSH.
        logger.exception("Chat endpoint failed")
        raise HTTPException(
            status_code=500,
            detail=f"Chat generation failed: {type(e).__name__}: {e}",
        )
