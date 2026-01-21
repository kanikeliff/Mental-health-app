from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class EmotionInference:
    """
    Lightweight emotion inference.
    Rule-based fallback (demo-safe).
    """

    def __init__(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        mapping_path = data_dir / "label_mapping.json"

        if mapping_path.exists():
            with mapping_path.open("r", encoding="utf-8") as f:
                self.label_mapping = json.load(f)
        else:
            self.label_mapping = {
                "happy": 0,
                "sad": 1,
                "neutral": 2,
                "stressed": 3,
                "anxious": 4,
                "angry": 5,
            }

    def classify(self, text: str) -> Dict:
        t = text.lower()

        if any(k in t for k in ["happy", "great", "good", "awesome"]):
            emotion = "happy"
        elif any(k in t for k in ["sad", "down", "depressed"]):
            emotion = "sad"
        elif any(k in t for k in ["stress", "overwhelm", "tired"]):
            emotion = "stressed"
        elif any(k in t for k in ["anxious", "panic", "worried"]):
            emotion = "anxious"
        elif any(k in t for k in ["angry", "mad", "furious"]):
            emotion = "angry"
        else:
            emotion = "neutral"

        return {
            "emotion": emotion,
            "label": self.label_mapping.get(emotion, -1),
            "confidence": 0.75
        }


# ✅ SIMPLE FUNCTION API (senin çağırdığın şey)
_engine = EmotionInference()

def predict_emotion(text: str) -> Dict:
    return _engine.classify(text)
