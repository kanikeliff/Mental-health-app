from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict


class ChatIn(BaseModel):
    # I keep clientMessageId optional; iOS can send it if it wants stable IDs.
    userText: str = Field(..., min_length=1)
    clientMessageId: Optional[str] = None


class ChatOut(BaseModel):
    assistantText: str
    metadata: Dict = {}
