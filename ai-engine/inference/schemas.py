# inference/schemas.py
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class RecommendRequest(BaseModel):
    user_id: str
    k: int = 10


class RecItem(BaseModel):
    item_id: str
    score: float
    explanation: Optional[str] = None


class RecommendResponse(BaseModel):
    user_id: str
    results: List[RecItem]