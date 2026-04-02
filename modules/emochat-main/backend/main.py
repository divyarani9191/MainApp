"""
EmoHeal - Main FastAPI Application
Serves both API and React frontend static files.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import validate_config
from app.database.db import connect_to_mongo, close_mongo_connection, create_indexes
from app.routes.chat import router as chat_router
from app.routes.history import router as history_router

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

validate_config()

app = FastAPI(
    title="EmoHeal API",
    version="1.0.0",
    description="AI-powered emotional support chatbot"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────
app.include_router(chat_router)
app.include_router(history_router)

# ── Serve React frontend build ────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str = ""):
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)

# ── Startup & Shutdown ────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    await create_indexes()
    logger.info("🚀 EmoHeal is running at http://localhost:8000")


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()
    logger.info("🔌 EmoHeal stopped")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EmoHeal API"}