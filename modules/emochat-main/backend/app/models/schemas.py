"""
EmoHeal - Data Schemas
Pydantic models for request validation and response serialization
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================================
# AUTH SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    """Request body for user registration"""
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Aditya Sharma",
                "email": "aditya@example.com",
                "password": "mypassword123"
            }
        }


class LoginRequest(BaseModel):
    """Request body for user login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "aditya@example.com",
                "password": "mypassword123"
            }
        }


class TokenResponse(BaseModel):
    """Response returned after successful login or register"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str


class UserResponse(BaseModel):
    """Public user profile (no password)"""
    user_id: str
    name: str
    email: str
    created_at: datetime
    last_active: datetime


# ============================================================
# MESSAGE SCHEMAS
# ============================================================

class MessageIn(BaseModel):
    """Incoming WebSocket message from user"""
    message: str = Field(..., min_length=1, max_length=2000)


class MessageOut(BaseModel):
    """Outgoing message to user"""
    type: str                          # bot_response | crisis_alert | off_topic
    message: str
    crisis_level: Optional[str] = "low"
    mood_detected: Optional[str] = None
    timestamp: str


# ============================================================
# MOOD SCHEMAS
# ============================================================

class MoodEntry(BaseModel):
    """A single mood data point — written by any feature"""
    user_id: str
    mood: str                          # happy | sad | anxious | calm | angry | neutral
    score: float = Field(..., ge=0.0, le=1.0)
    source: str                        # camera | voice | chatbot
    timestamp: datetime = Field(default_factory=datetime.now)


class MoodSummary(BaseModel):
    """Mood summary returned to frontend"""
    latest_mood: Optional[str]
    latest_score: Optional[float]
    history: List[dict]


# ============================================================
# CRISIS SCHEMAS
# ============================================================

class CrisisAlert(BaseModel):
    """Stored when crisis is detected"""
    user_id: str
    session_id: str
    trigger_message: str
    crisis_level: str                  # medium | high
    reasoning: str
    resources_shown: List[str]
    resolved: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================
# CHAT HISTORY SCHEMAS
# ============================================================

class ChatSession(BaseModel):
    """A single chat session"""
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    overall_mood: Optional[str]
    crisis_flagged: bool = False
    message_count: int = 0


class ChatHistoryResponse(BaseModel):
    """Returned when fetching past sessions"""
    sessions: List[ChatSession]
    total: int