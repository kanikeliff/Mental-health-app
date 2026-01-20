from typing import Tuple, Dict

# I keep a tiny safety keyword list so demo doesn't output dangerous stuff.
# This is NOT perfect safety, but it's a good baseline for grading.
_RISKY_BITS = [
    "suicide", "kill myself", "end my life", "self harm",
    "intihar", "kendimi öldür", "ölmek istiyorum"
]


def _looks_dangerous(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in _RISKY_BITS)


def cook_assistant_reply(user_text: str) -> Tuple[str, Dict]:
    """
    This is my temporary brain.
    I did this because ai-engine integration might change,
    but backend MUST work today.
    """

    if _looks_dangerous(user_text):
        return (
            "I’m really sorry you’re feeling this way. If you’re in immediate danger or feel like "
            "you might hurt yourself, please contact your local emergency number right now or go "
            "to the nearest emergency room. If you can, reach out to someone you trust.",
            {"safety": {"flagged": True, "category": "self-harm"}, "debug": {"fallbackAI": True}},
        )

    low = user_text.lower()
    if "stress" in low:
        reply = "That sounds heavy. What’s been the biggest stress trigger recently?"
    elif "sleep" in low:
        reply = "Sleep impacts mood a lot. What has your sleep been like this week?"
    elif "anx" in low or "panic" in low:
        reply = "I’m here with you. What thought is looping the most right now?"
    else:
        reply = "I hear you. Can you walk me through what happened today?"

    return reply, {"safety": {"flagged": False, "category": None}, "debug": {"fallbackAI": True}}
