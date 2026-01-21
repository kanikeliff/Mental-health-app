from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatIn(BaseModel):
    # I expect iOS to send the user's message in this field.
    userText: str = Field(..., min_length=1)

    # I keep these optional so the frontend can evolve without breaking the API.
    conversationId: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    clientMessageId: Optional[str] = None


class ChatOut(BaseModel):
    # I return the assistant's reply here.
    assistantText: str

    # I attach extra info for debugging and UI decisions (tags/tone/etc).
    metadata: Dict[str, Any] = {}
