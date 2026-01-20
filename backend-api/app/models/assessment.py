from pydantic import BaseModel
from typing import Dict, Optional


class AssessmentIn(BaseModel):
    # I keep this generic because assessments can change.
    kind: str
    answers: Dict
    score: Optional[float] = None
