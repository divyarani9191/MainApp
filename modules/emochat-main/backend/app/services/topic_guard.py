"""
EmoHeal - Topic Guard Service
Uses Groq API (llama-3.3-70b) to determine if a user message is within
the scope of mental/emotional health support.
No keywords. Fully model-driven.
"""

import json
import logging
from groq import Groq
from app.config import GROQ_API_KEY

logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


async def check_topic_scope(message: str, conversation_history: list) -> dict:
    """
    Determines if a message is relevant to emotional/mental health support.

    Returns:
        {
            "is_off_topic": bool,
            "confidence": float,
            "reason": str,
            "redirect_response": str
        }
    """
    history_text = ""
    if conversation_history:
        recent = conversation_history[-4:]
        history_text = "\n".join([
            f"User: {h['content']}" if h['role'] == 'user'
            else f"EmoHeal: {h['content']}"
            for h in recent
        ])

    prompt = f"""You are a scope classifier for EmoHeal, an AI emotional support chatbot.

Your job is to decide if the user's message is within scope.

IN SCOPE (handle normally):
- Emotions, feelings, mood, mental health
- Anxiety, depression, stress, loneliness, grief
- Relationships, family, work pressure, self-esteem
- Crisis, self-harm thoughts, suicidal ideation
- Personal struggles, trauma, life problems
- Anything that indirectly reflects emotional state

OUT OF SCOPE (redirect politely):
- Pure factual queries: math, coding, science homework
- Entertainment: movies, sports scores, gaming tips
- Commerce: shopping, prices, product recommendations
- Completely unrelated small talk with no emotional context

IMPORTANT RULES:
- When in doubt, treat as IN SCOPE. It is safer to engage than to reject.
- "I feel like eating pizza" → IN SCOPE (emotional expression)
- "What is 2+2?" → OUT OF SCOPE (pure factual)
- Even indirect emotional expressions should be treated as in scope.

Conversation context:
{history_text if history_text else "No prior conversation"}

User's message: "{message}"

Respond ONLY in this exact JSON format, no extra text, no markdown:
{{
  "is_off_topic": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "one sentence explanation",
  "redirect_response": "a warm brief message redirecting to emotional topics (only if is_off_topic is true, otherwise empty string)"
}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        logger.info(f"Topic check: off_topic={result['is_off_topic']}, confidence={result['confidence']}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Topic guard JSON parse error: {e}")
        return {
            "is_off_topic": False,
            "confidence": 0.0,
            "reason": "Parse error — defaulting to in-scope",
            "redirect_response": ""
        }
    except Exception as e:
        logger.error(f"Topic guard error: {e}")
        return {
            "is_off_topic": False,
            "confidence": 0.0,
            "reason": "Service error — defaulting to in-scope",
            "redirect_response": ""
        }