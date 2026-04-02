# 🌿 EmoHeal — Psychiatric Chatbot

AI-powered emotional support chatbot with crisis detection, mood tracking, and therapeutic responses.

---

## 🚀 Quick Start

### Option A — One click (Windows)
```
Double-click start-all.bat
```

### Option B — Manual

**Backend:**
```powershell
cd backend
venv\Scripts\activate
python run.py
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

Then open **http://localhost:3000**

---

## 📁 Project Structure

```
emoheal/
├── backend/
│   ├── main.py
│   ├── run.py
│   ├── .env                    ← never commit this
│   └── app/
│       ├── config.py
│       ├── database/
│       │   └── db.py
│       ├── models/
│       │   └── schemas.py
│       ├── routes/
│       │   ├── auth.py
│       │   ├── chat.py
│       │   └── history.py
│       └── services/
│           ├── auth_service.py
│           ├── topic_guard.py
│           ├── crisis_detector.py
│           └── ai_therapist.py
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── main.jsx
        ├── index.css
        ├── App.jsx
        ├── api/
        │   └── client.js
        ├── context/
        │   └── AuthContext.jsx
        ├── pages/
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Chat.jsx
        │   └── History.jsx
        └── components/
            ├── Navbar.jsx
            ├── ChatBubble.jsx
            └── CrisisAlert.jsx
```

---

## ⚙️ Environment Setup

Create `backend/.env`:
```
MONGODB_URL=mongodb+srv://emoheal_team:password@cluster.mongodb.net/
DB_NAME=emoheal
JWT_SECRET=your_strong_secret_here
JWT_EXPIRE_HOURS=24
GROQ_API_KEY=gsk_your_groq_key_here
```

---

## 📦 Install Dependencies

**Backend:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |
| WS | `/ws/chat/{user_id}?token=<jwt>` | Real-time chat |
| GET | `/api/history/sessions` | All chat sessions |
| GET | `/api/history/messages/{session_id}` | Session messages |
| GET | `/api/history/mood-summary` | Mood trends |
| GET | `/api/history/latest-mood` | Latest mood |
| GET | `/api/history/crisis-alerts` | Crisis alerts |

---

## 🤖 AI Pipeline

```
User Message
    ↓
Topic Guard      → off-topic? redirect politely
    ↓
Crisis Detector  → high? show crisis alert + helplines
    ↓
AI Therapist     → generate warm therapeutic response
    ↓
Save to MongoDB + Send to user
```

All powered by **Groq API (llama-3.3-70b)** — no hardcoded keywords.

---

## 🆘 Crisis Helplines (India)

- **iCall:** 9152987821
- **Vandrevala Foundation:** 1860-2662-345
- **Emergency:** 112

---

## 👥 Team

Built as part of the EmoHeal emotional companion platform.