from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# --- DEMO SAFETY BASELINE (lightweight heuristic) ---
_RISKY_BITS = [
    "suicide", "kill myself", "end my life", "self harm", "self-harm",
    "intihar", "kendimi öldür", "ölmek istiyorum", "kendime zarar", "kendimi kes"
]


def _looks_dangerous(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in _RISKY_BITS)


def _fallback_rule_based_reply(user_text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Temporary brain: rule-based fallback.
    Goal: backend MUST work even if ai-engine is missing/broken.
    """
    if _looks_dangerous(user_text):
        return (
            "I’m really sorry you’re feeling this way. If you’re in immediate danger or feel like "
            "you might hurt yourself, please contact your local emergency number right now or go "
            "to the nearest emergency room. If you can, reach out to someone you trust.",
            {"safety": {"flagged": True, "category": "self-harm"}},
        )

    low = (user_text or "").lower()
    if "stress" in low:
        reply = "That sounds heavy. What’s been the biggest stress trigger recently?"
        tags = ["stress"]
    elif "sleep" in low:
        reply = "Sleep impacts mood a lot. What has your sleep been like this week?"
        tags = ["sleep"]
    elif "anx" in low or "panic" in low:
        reply = "I’m here with you. What thought is looping the most right now?"
        tags = ["anxiety"]
    else:
        reply = "I hear you. Can you walk me through what happened today?"
        tags = []

    return reply, {"safety": {"flagged": False, "category": None}, "tags": tags}


def generate_chat_reply(
    user_id: str,
    user_text: str,
    chat_context: Optional[List[Dict[str, Any]]] = None,
    mood_context: Optional[List[Dict[str, Any]]] = None,
    k: int = 10,
) -> Dict[str, Any]:
    """
    Backend-facing function for chat. Always returns stable JSON.
    1) Try ai-engine (if available)
    2) Fallback to rule-based response
    """

    # --- Fast safety short-circuit (even before AI) ---
    if _looks_dangerous(user_text):
        reply, meta = _fallback_rule_based_reply(user_text)
        return {
            "assistant_reply": reply,
            "safety": meta["safety"],
            "tags": meta.get("tags", []),
            "tone": "supportive",
            "follow_up_questions": [],
            "debug": {"fallbackAI": True, "provider": "rule_based"},
        }

    # --- Try ai-engine if integrated ---
    try:
        # If you already created app/services/ai_bridge.py, this will work.
        # If not, it'll jump to fallback cleanly.
        from app.services.ai_bridge import get_recommendations  # noqa: F401

        # For now your ai-engine work is recommender; chat AI may come later.
        # You can still enrich response with recs or keep it simple.
        # Example: call recs (optional)
        # recs = get_recommendations(user_id=user_id, k=k)

        # If you later add ai-engine chat generation, call it here instead.
        # For now: just fallback style but mark provider=backend
        reply, meta = _fallback_rule_based_reply(user_text)
        return {
            "assistant_reply": reply,
            "safety": meta["safety"],
            "tags": meta.get("tags", []),
            "tone": "supportive",
            "follow_up_questions": [],
            "debug": {"fallbackAI": True, "provider": "rule_based_with_bridge_available"},
        }

    except Exception as e:
        # --- Fallback ---
        reply, meta = _fallback_rule_based_reply(user_text)
        return {
            "assistant_reply": reply,
            "safety": meta["safety"],
            "tags": meta.get("tags", []),
            "tone": "supportive",
            "follow_up_questions": [],
            "debug": {"fallbackAI": True, "provider": "rule_based", "error": str(e)},
        }