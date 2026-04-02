"""
EmoHeal - Single File Launcher
Run this ONE file to start the entire chatbot.

Usage:
    python run.py

What it does:
    1. Checks Python dependencies
    2. Builds the React frontend (npm run build)
    3. Starts FastAPI which serves the built frontend
    4. Opens browser automatically

Visit: http://localhost:8000
"""

import sys
import os
import subprocess
import time
#import webbrowser
import importlib.util
import threading

# ── Add backend/ to Python path ───────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")


def check_pkg(name):
    return importlib.util.find_spec(name) is not None


def run_cmd(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, shell=True)


def check_node():
    r = subprocess.run("node --version", shell=True, capture_output=True)
    return r.returncode == 0


# ── STEP 1: Python dependencies ───────────────────────────
print("\n Checking Python dependencies...")
required = ["fastapi", "uvicorn", "motor", "groq", "dotenv", "jose", "passlib"]
missing = [p for p in required if not check_pkg(p)]
if missing:
    print(f" Installing: {', '.join(missing)}")
    run_cmd(
        f"{sys.executable} -m pip install fastapi uvicorn motor pymongo pydantic "
        f"\"pydantic[email]\" python-jose[cryptography] bcrypt passlib groq "
        f"python-dotenv websockets httpx"
    )
else:
    print("OK Python dependencies installed")


# ── STEP 2: Check .env ────────────────────────────────────
env_file = os.path.join(BASE_DIR, ".env")
if not os.path.exists(env_file):
    print("\nERROR: .env file not found!")
    print(f"  Create it at: {env_file}")
    print("  Required:")
    print("  MONGODB_URL=mongodb+srv://...")
    print("  DB_NAME=emoheal")
    print("  JWT_SECRET=any_random_string")
    print("  GROQ_API_KEY=gsk_...")
    sys.exit(1)
print("OK .env file found")


# ── STEP 3: Build frontend ────────────────────────────────
if not os.path.exists(FRONTEND_DIR):
    print("\nWARNING: frontend/ folder not found - skipping build")
elif not check_node():
    print("\nWARNING: Node.js not found - skipping frontend build")
    print("  Install from https://nodejs.org")
else:
    print("\n Building React frontend...")
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("  Installing npm packages (first run, ~1 min)...")
        result = run_cmd("npm install", cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print("ERROR: npm install failed")
            sys.exit(1)
    result = run_cmd("npm run build", cwd=FRONTEND_DIR)
    if result.returncode != 0:
        print("ERROR: Frontend build failed")
        print("  Run 'npm run build' in frontend/ to see full error")
        sys.exit(1)
    print("OK Frontend built")


# ── STEP 4: Open browser + start server ──────────────────
print("\n" + "="*45)
print("  EmoHeal is starting...")
print("  URL:      http://localhost:8000")
print("  API docs: http://localhost:8000/docs")
print("  Stop:     Ctrl+C")
print("="*45 + "\n")

#def open_browser():
  #  time.sleep(2.5)
   # webbrowser.open("http://localhost:8000")

#threading.Thread(target=open_browser, daemon=True).start()

import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)