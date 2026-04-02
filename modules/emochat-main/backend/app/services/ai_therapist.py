"""
EmoHeal - AI Therapist Service
Uses Groq API (llama-3.3-70b) to generate warm, contextual,
therapeutic responses. No templates. No scripts. Fully model-driven.
"""

import logging
from groq import Groq
from app.config import GROQ_API_KEY

logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


async def generate_therapeutic_response(
    message: str,
    mood: str,
    crisis_level: str,
    conversation_history: list
) -> str:
    """
    Generates a therapeutic response using Groq.

    Returns:
        A warm, contextual therapeutic response string
    """
    history_text = ""
    if conversation_history:
        recent = conversation_history[-8:]
        history_text = "\n".join([
            f"User: {h['content']}" if h['role'] == 'user'
            else f"EmoHeal: {h['content']}"
            for h in recent
        ])

    crisis_instruction = ""
    if crisis_level == "medium":
        crisis_instruction = """
The user is showing signs of significant distress.
- Validate their feelings deeply before anything else
- Gently mention that speaking to a counselor or trusted person can help
- Do not push too hard — just plant the seed
- Keep your tone extra warm and patient"""

    elif crisis_level == "high":
        crisis_instruction = """
The user may be in crisis. A separate crisis alert has already been shown to them.
- Your role now is to be a calm, stabilizing presence
- Acknowledge their pain without minimizing it
- Encourage them to reach out to someone they trust or call a helpline
- Do not lecture or give advice — just be present with them
- Never say anything that could increase distress"""

    prompt = f"""You are EmoHeal, a compassionate AI emotional support companion.
You provide a safe, non-judgmental space for people to express their feelings.

YOUR APPROACH:
- Use evidence-based techniques: active listening, CBT, motivational interviewing
- Be warm, human, and conversational — never clinical or robotic
- Reflect back what the user said to show you truly heard them
- Ask ONE thoughtful follow-up question when appropriate (not always)
- Never diagnose, never prescribe, never give medical advice
- Keep responses concise: 2-4 sentences usually, 5-6 for complex emotions
- Adapt your tone: gentle for sadness, grounding for anxiety,
  validating for anger, encouraging for hopelessness

USER CONTEXT:
- Detected mood: {mood}
- Crisis level: {crisis_level}
{crisis_instruction}

Conversation so far:
{history_text if history_text else "This is the start of the conversation"}

Latest message from user: "{message}"

Write your response as EmoHeal. Just the response text — no labels, no quotes, no preamble."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        logger.info(f"Therapist response generated: mood={mood}, crisis={crisis_level}, chars={len(reply)}")
        return reply

    except Exception as e:
        logger.error(f"AI therapist error: {e}")
        return (
            "I'm here with you. It sounds like you're going through something difficult. "
            "Would you like to tell me more about what's on your mind?"
        )