import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a calm, supportive mental health assistant.
You listen carefully, validate emotions, and respond briefly but empathetically.
You never diagnose or give medical advice.
"""

def generate_chat_reply(user_message: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "AI service is not configured."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()
