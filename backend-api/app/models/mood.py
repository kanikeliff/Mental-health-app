from pydantic import BaseModel, Field
from typing import Optional


class MoodIn(BaseModel):
    # iOS already writes moods directly to Firestore, but I keep this for API parity.
    moodScore: int = Field(..., ge=1, le=5)
    note: Optional[str] = ""
