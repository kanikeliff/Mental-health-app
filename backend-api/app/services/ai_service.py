# backend-api/app/services/ai_service.py
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import httpx
from openai import OpenAI


def _rule_based_reply(user_text: str) -> Dict[str, Any]:
    # I keep a tiny fallback so the app never "silently fails".
    # This is NOT real AI, just a safety net.
    text = user_text.strip().lower()
    if "anx" in text or "overwhelm" in text or "stress" in text:
        assistant = "I hear you. Want to tell me what’s making it feel the most overwhelming right now?"
        tags = ["stress"]
    else:
        assistant = "I’m here with you. What’s on your mind today?"
        tags = []

    return {
        "assistantText": assistant,
        "metadata": {
            "tags": tags,
            "tone": "supportive",
            "debug": {"provider": "rule_based"},
        },
    }


def generate_chat_reply(
    user_text: str,
    *,
    user_id: str,
    conversation_id: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    I generate a chat reply here.
    - If OPENAI_API_KEY exists, I try real LLM.
    - If anything goes wrong, I fall back to rule-based so the endpoint still responds.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        # I don't want prod to crash if the key is missing.
        return _rule_based_reply(user_text)

    # I keep timeouts tight because Render free instances can hang easily.
    timeout = httpx.Timeout(connect=10.0, read=35.0, write=10.0, pool=10.0)

    started = time.time()

    try:
        # IMPORTANT: OpenAI() must be called with keyword args (api_key=...).
        client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(timeout=timeout),
        )

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are a supportive mental health companion. "
                    "Be kind, practical, and ask one short follow-up question. "
                    "Do NOT claim to be a licensed therapist. "
                    "If user seems in immediate danger, advise contacting local emergency services."
                ),
            }
        ]

        # I optionally include short chat history for continuity.
        if history:
            for m in history[-10:]:
                role = m.get("role")
                content = m.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_text})

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=220,
        )

        assistant_text = (resp.choices[0].message.content or "").strip()
        if not assistant_text:
            # I treat empty output as failure and use fallback.
            return _rule_based_reply(user_text)

        took_ms = int((time.time() - started) * 1000)

        return {
            "assistantText": assistant_text,
            "metadata": {
                "tags": [],
                "tone": "supportive",
                "debug": {
                    "provider": "openai",
                    "model": model,
                    "tookMs": took_ms,
                },
            },
        }

    except Exception:
        # I don't want one provider failure to kill the whole endpoint.
        return _rule_based_reply(user_text)
