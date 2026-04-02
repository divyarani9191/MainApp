"""
EmoHeal - Chat Route
WebSocket endpoint — no auth required, session ID auto-generated.
Pipeline: Topic Guard → Crisis Detector → AI Therapist → MongoDB
"""

import json
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.db import get_database
from app.services.topic_guard import check_topic_scope
from app.services.crisis_detector import detect_crisis, get_crisis_resources
from app.services.ai_therapist import generate_therapeutic_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    No auth — session ID is auto-generated per connection.

    Connect: ws://localhost:8000/ws/chat
    Send:    { "message": "I feel anxious today" }
    Receive: { "type": "bot_response", "message": "...", "mood": "...", ... }
    """
    await websocket.accept()
    db = await get_database()

    # Auto-generate session identity
    session_id = str(uuid.uuid4())
    user_id = f"guest_{session_id[:8]}"
    conversation_history = []

    # Create session record in DB
    await db.chat_sessions.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "started_at": datetime.now(),
        "ended_at": None,
        "overall_mood": "neutral",
        "crisis_flagged": False,
        "message_count": 0
    })

    try:
        # ── Welcome message ───────────────────────────────
        welcome = (
            "Hello! I'm EmoHeal, your emotional support companion. 🌿\n"
            "This is a safe space to share how you're feeling. "
            "How are you doing today?"
        )
        await websocket.send_json({
            "type": "bot_response",
            "message": welcome,
            "mood": "neutral",
            "crisis_level": "low",
            "timestamp": datetime.now().isoformat()
        })

        await db.messages.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "role": "bot",
            "content": welcome,
            "mood_detected": "neutral",
            "crisis_level": "low",
            "is_off_topic": False,
            "timestamp": datetime.now()
        })

        # ── Main chat loop ────────────────────────────────
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()

            if not user_message:
                continue

            # Save user message
            await db.messages.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "role": "user",
                "content": user_message,
                "mood_detected": None,
                "crisis_level": None,
                "is_off_topic": False,
                "timestamp": datetime.now()
            })

            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # ── STEP 1: TOPIC GUARD ───────────────────────
            topic_result = await check_topic_scope(user_message, conversation_history)

            if topic_result["is_off_topic"] and topic_result["confidence"] >= 0.80:
                redirect_msg = topic_result["redirect_response"] or (
                    "I'm here to support you emotionally. "
                    "Is there something on your mind you'd like to talk about?"
                )
                await websocket.send_json({
                    "type": "off_topic",
                    "message": redirect_msg,
                    "timestamp": datetime.now().isoformat()
                })
                await db.messages.insert_one({
                    "user_id": user_id,
                    "session_id": session_id,
                    "role": "bot",
                    "content": redirect_msg,
                    "mood_detected": "neutral",
                    "crisis_level": "low",
                    "is_off_topic": True,
                    "timestamp": datetime.now()
                })
                conversation_history.append({"role": "bot", "content": redirect_msg})
                continue

            # ── STEP 2: CRISIS DETECTION ──────────────────
            crisis_result = await detect_crisis(user_message, conversation_history)
            crisis_level = crisis_result["level"]
            mood = crisis_result["mood"]

            # Save mood to shared collection
            await db.moods.insert_one({
                "user_id": user_id,
                "mood": mood,
                "score": crisis_result["confidence"],
                "source": "chatbot",
                "timestamp": datetime.now()
            })

            # Handle crisis
            if crisis_level in ["medium", "high"]:
                resources = get_crisis_resources()
                await db.crisis_alerts.insert_one({
                    "user_id": user_id,
                    "session_id": session_id,
                    "trigger_message": user_message,
                    "crisis_level": crisis_level,
                    "reasoning": crisis_result["reasoning"],
                    "resources_shown": list(resources.keys()),
                    "resolved": False,
                    "timestamp": datetime.now()
                })
                await websocket.send_json({
                    "type": "crisis_alert",
                    "level": crisis_level,
                    "message": crisis_result["crisis_response"],
                    "resources": resources,
                    "timestamp": datetime.now().isoformat()
                })
                await db.chat_sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"crisis_flagged": True}}
                )
                if crisis_level == "high":
                    await db.messages.insert_one({
                        "user_id": user_id,
                        "session_id": session_id,
                        "role": "bot",
                        "content": crisis_result["crisis_response"],
                        "mood_detected": mood,
                        "crisis_level": crisis_level,
                        "is_off_topic": False,
                        "timestamp": datetime.now()
                    })
                    conversation_history.append({
                        "role": "bot",
                        "content": crisis_result["crisis_response"]
                    })
                    continue

            # ── STEP 3: GENERATE RESPONSE ─────────────────
            bot_response = await generate_therapeutic_response(
                user_message, mood, crisis_level, conversation_history
            )

            # Save bot response
            await db.messages.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "role": "bot",
                "content": bot_response,
                "mood_detected": mood,
                "crisis_level": crisis_level,
                "is_off_topic": False,
                "timestamp": datetime.now()
            })

            await db.chat_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"overall_mood": mood}, "$inc": {"message_count": 1}}
            )

            conversation_history.append({"role": "bot", "content": bot_response})

            await websocket.send_json({
                "type": "bot_response",
                "message": bot_response,
                "mood": mood,
                "crisis_level": crisis_level,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"Chat: session={session_id[:8]}, mood={mood}, crisis={crisis_level}")

    except WebSocketDisconnect:
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"ended_at": datetime.now()}}
        )
        logger.info(f"Session {session_id[:8]} ended")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Something went wrong. Please refresh and try again."
            })
            await websocket.close()
        except Exception:
            pass