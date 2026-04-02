"""
EmoHeal - Crisis Detector Service
Uses Groq API (llama-3.3-70b) to assess suicidal ideation,
self-harm intent, and severe emotional distress.
No keywords. Fully model-driven.
"""

import json
import logging
from groq import Groq
from app.config import GROQ_API_KEY

logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# Crisis resources shown to user
CRISIS_RESOURCES = {
    "iCall (India)": "9152987821",
    "Vandrevala Foundation": "1860-2662-345",
    "iCall Chat": "icallhelpline.org",
    "Emergency": "112"
}


async def detect_crisis(message: str, conversation_history: list) -> dict:
    """
    Analyzes a message for crisis signals using Groq.

    Returns:
        {
            "level": "low" | "medium" | "high",
            "confidence": float,
            "reasoning": str,
            "mood": str,
            "crisis_response": str
        }
    """
    history_text = ""
    if conversation_history:
        recent = conversation_history[-6:]
        history_text = "\n".join([
            f"User: {h['content']}" if h['role'] == 'user'
            else f"EmoHeal: {h['content']}"
            for h in recent
        ])

    prompt = f"""You are a mental health crisis assessment specialist for EmoHeal.
Carefully analyze the message below for signs of crisis, suicidal ideation, or severe distress.

CRISIS LEVELS:
- "high": Immediate risk — explicit suicidal ideation, self-harm intent, a plan to end life,
  statements like wanting to die or disappear permanently
- "medium": Significant distress — hopelessness, passive death wish ("I wish I wasn't here"),
  severe depression, emotional breakdown
- "low": General emotional difficulty — sadness, anxiety, stress, relationship issues,
  no immediate risk

MOOD DETECTION — identify one primary mood from this list only:
happy | sad | anxious | calm | angry | hopeless | lonely | overwhelmed | neutral

IMPORTANT RULES:
- Consider context, metaphors, indirect expressions and cultural nuance
- Do NOT rely on specific words alone — consider overall tone and meaning
- "I just want everything to stop" in a distressed context = high risk
- Err on the side of caution: when unsure between medium and high, choose high
- Your crisis_response must be warm, non-judgmental, and human — never robotic

Conversation context:
{history_text if history_text else "First message"}

Latest message: "{message}"

Respond ONLY in this exact JSON format, no extra text, no markdown:
{{
  "level": "low" or "medium" or "high",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief clinical reasoning in one sentence",
  "mood": "one mood word from the list above",
  "crisis_response": "warm empathetic message for medium/high crisis, empty string for low"
}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        logger.info(f"Crisis check: level={result['level']}, mood={result['mood']}, confidence={result['confidence']}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Crisis detector JSON parse error: {e}")
        return {
            "level": "low",
            "confidence": 0.0,
            "reasoning": "Parse error",
            "mood": "neutral",
            "crisis_response": ""
        }
    except Exception as e:
        logger.error(f"Crisis detector error: {e}")
        return {
            "level": "low",
            "confidence": 0.0,
            "reasoning": "Service error",
            "mood": "neutral",
            "crisis_response": ""
        }


def get_crisis_resources() -> dict:
    """Returns the crisis helpline resources to show the user"""
    return CRISIS_RESOURCES