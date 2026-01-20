# backend-api/app/services/ai_bridge.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Path layout (based on your screenshot):
#   REPO_ROOT/
#     backend-api/
#       app/
#         services/
#           ai_bridge.py  <-- this file
#     ai-engine/
#       inference/
#       training/
#       models/
REPO_ROOT = Path(__file__).resolve().parents[3]   # services -> app -> backend-api -> REPO_ROOT
AI_ENGINE_DIR = REPO_ROOT / "ai-engine"

if not AI_ENGINE_DIR.exists():
    raise RuntimeError(f"ai-engine folder not found at: {AI_ENGINE_DIR}")

# Make ai-engine importable as a "root" so we can do: from inference.predict import recommend
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))


# -------- Recommendation bridge --------
def get_recommendations(
    user_id: str,
    k: int = 10,
    model_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls ai-engine recommendation inference and returns JSON-serializable dict.

    model_dir:
      - default uses ai-engine/models/recommendation/latest (relative to ai-engine root)
      - you can pass an absolute path if you want
    """
    if model_dir is None:
        model_dir = "models/recommendation/latest"

    # Import here (lazy import) so backend can still boot even if ai-engine deps are missing,
    # until this function is actually called.
    from inference.predict import recommend  # type: ignore

    resp = recommend(user_id=user_id, k=k, model_dir=model_dir)
    return resp.model_dump()


# -------- Optional: Health check helper --------
def ai_engine_healthcheck() -> Dict[str, Any]:
    """
    Basic sanity check: verifies ai-engine exists + model folder presence.
    Does NOT guarantee model files are correct; just a quick debug tool.
    """
    model_path = AI_ENGINE_DIR / "models" / "recommendation" / "latest"
    return {
        "ai_engine_dir": str(AI_ENGINE_DIR),
        "model_dir": str(model_path),
        "model_dir_exists": model_path.exists(),
    }
