from __future__ import annotations

from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


# I keep these schemas super small on purpose.
# I only define what the API actually uses at runtime.

class ChatIn(BaseModel):
    # I expect iOS to send the user's message here.
    userText: str = Field(..., min_length=1)
    # I allow an optional client message id so I can debug and dedupe later.
    clientMessageId: Optional[str] = None


class ChatOut(BaseModel):
    # I return the assistant text back to the client.
    assistantText: str
    # I keep metadata flexible for future: tags, safety, debug, etc.
    metadata: Dict[str, Any] = {}
