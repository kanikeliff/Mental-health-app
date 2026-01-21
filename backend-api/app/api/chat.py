from fastapi import APIRouter, Header, HTTPException

# I import this at module level on purpose.
# If I import it inside the function, Python may think it's a local variable
# and that caused the UnboundLocalError we saw in Render logs.
from app.services.ai_service import generate_chat_reply

# I always extract the user identity from Firebase token (or DEV bypass),
# never from request body, because I don't trust client input.
from app.services.firebase_service import verify_firebase_bearer

# These schemas define the exact API contract for iOS.
# Keeping them explicit avoids silent breaking changes.
from app.models.schemas import ChatIn, ChatOut
# If this import ever fails, I know the schema path changed.


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn, authorization: str = Header(default="")) -> ChatOut:
    # 1) Authentication step
    # I do auth first so unauthorized users never hit AI or database logic.
    try:
        uid = verify_firebase_bearer(authorization)
    except Exception:
        # I return a clean 401 so the client knows this is an auth issue,
        # not a random backend crash.
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase token"
        )

    # 2) Generate AI reply
    # This function decides whether to use OpenAI or fallback logic.
    # I wrap it in try/except so provider errors don't crash the server.
    try:
        result = generate_chat_reply(
            user_text=payload.userText,
            user_id=uid,
            client_message_id=payload.clientMessageId,
        )
    except Exception as e:
        # I intentionally don't leak internal error details to the client.
        # Render logs already show the real traceback.
        raise HTTPException(
            status_code=500,
            detail=f"Chat generation failed: {type(e).__name__}"
        )

    # 3) Build API response
    # I always return assistantText + metadata in a stable shape
    # so the iOS side never has to guess.
    return ChatOut(
        assistantText=result.get("assistantText", ""),
        metadata=result.get("metadata", {}) or {},
    )
