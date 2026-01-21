from fastapi import APIRouter, Header, HTTPException
from app.services.ai_service import generate_chat_reply
from app.services.firebase_service import verify_firebase_bearer

# Bu modeller projende nerede tanımlıysa ona göre import et.
# Çoğu projede şu ikisinden biri olur:
# from app.models.schemas import ChatIn, ChatOut
# from app.schemas import ChatIn, ChatOut

from app.models.schemas import ChatIn, ChatOut  # <-- Eğer bu patlarsa alttaki alternatifi dene
# from app.schemas import ChatIn, ChatOut


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn, authorization: str = Header(default="")) -> ChatOut:
    # 1) Auth (Firebase / dev bypass firebase_service içinde)
    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        # Render'da Authorization "anything" gönderince 401 gelmesi normal (DEV_BYPASS_AUTH yoksa)
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    # 2) AI reply üret
    try:
        result = generate_chat_reply(
            user_text=payload.userText,
            user_id=uid,
            client_message_id=payload.clientMessageId,
        )
    except Exception as e:
        # AI provider / env problemi vs. -> 500 ama mesaj anlaşılır olsun
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {type(e).__name__}")

    # 3) Response
    return ChatOut(
        assistantText=result.get("assistantText", ""),
        metadata=result.get("metadata", {}) or {},
    )
