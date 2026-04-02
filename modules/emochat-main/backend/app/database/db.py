"""
EmoHeal - Database
Async MongoDB connection using Motor driver
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL, DB_NAME
import logging

logger = logging.getLogger(__name__)

# Global client instance (reused across requests)
_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """
    Opens the MongoDB connection.
    Called once on app startup.
    """
    global _client
    try:
        _client = AsyncIOMotorClient(MONGODB_URL)
        # Verify connection is alive
        await _client.admin.command("ping")
        logger.info("✅ Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise


async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    Called once on app shutdown.
    """
    global _client
    if _client:
        _client.close()
        logger.info("🔌 MongoDB connection closed")


async def get_database():
    """
    Returns the database instance.
    Use this in routes and services to access collections.

    Usage:
        db = await get_database()
        await db.users.find_one({"email": email})
    """
    if _client is None:
        raise RuntimeError("Database not initialised. Was connect_to_mongo() called?")
    return _client[DB_NAME]


async def create_indexes():
    """
    Creates indexes for performance and uniqueness constraints.
    Called once after connection on startup.
    """
    db = await get_database()

    # users — unique email
    await db.users.create_index("email", unique=True)

    # messages — fast lookup by user and session
    await db.messages.create_index("user_id")
    await db.messages.create_index("session_id")
    await db.messages.create_index([("user_id", 1), ("timestamp", -1)])

    # chat_sessions — fast lookup by user
    await db.chat_sessions.create_index("user_id")
    await db.chat_sessions.create_index([("user_id", 1), ("started_at", -1)])

    # crisis_alerts — fast lookup by user, filter unresolved
    await db.crisis_alerts.create_index("user_id")
    await db.crisis_alerts.create_index([("user_id", 1), ("resolved", 1)])

    logger.info("✅ Database indexes created")