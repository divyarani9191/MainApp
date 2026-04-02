"""
EmoHeal - History Routes (no auth)
GET /api/history/latest-mood  — latest mood (used by soul garden / music)
"""

from fastapi import APIRouter, Query
from app.database.db import get_database

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/latest-mood")
async def get_latest_mood(user_id: str = Query(...)):
    """
    Returns the user's most recent mood.
    Used by soul garden and music therapy to react to mood.
    Query param: ?user_id=guest_abc123
    """
    db = await get_database()

    latest = await db.moods.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )

    if not latest:
        return {"mood": "neutral", "score": 0.5, "source": "default"}

    return {
        "mood": latest["mood"],
        "score": latest["score"],
        "source": latest["source"],
        "timestamp": latest["timestamp"].isoformat()
    }