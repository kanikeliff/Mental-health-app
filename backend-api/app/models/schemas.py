from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# I keep these schemas super small on purpose.
# I only define what the API actually uses at runtime.

class ChatIn(BaseModel):
    # I expect iOS to send the user's message here.
    userText: str = Field(..., min_length=1)
    clientMessageId: Optional[str] = None


class ChatOut(BaseModel):
    # I return the assistant's text back to the client.
    assistantText: str
    # I keep metadata flexible because AI providers may return extra fields.
    metadata: Dict[str, Any] = Field(default_factory=dict)
