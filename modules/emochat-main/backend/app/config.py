"""
EmoHeal - Configuration
Loads all environment variables from .env file
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Always load from backend/.env regardless of where Python is run from
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ── MongoDB ──────────────────────────────────────────────
MONGODB_URL: str = os.getenv("MONGODB_URL", "")
DB_NAME: str = os.getenv("DB_NAME", "emoheal")

# ── JWT Auth ─────────────────────────────────────────────
JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# ── Groq AI ───────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


# ── Sanity check on startup ───────────────────────────────
def validate_config():
    missing = []
    if not MONGODB_URL:
        missing.append("MONGODB_URL")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if JWT_SECRET == "changeme":
        print("⚠️  WARNING: JWT_SECRET is using default value. Set a strong secret in .env")
    if missing:
        raise EnvironmentError(
            f"❌ Missing required environment variables: {', '.join(missing)}"
        )
    print("✅ Config loaded successfully")