// src/api/client.js
// Central API client — all backend calls go through here

import axios from "axios";

const BASE_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000";

// ── Axios instance ────────────────────────────────────────
const api = axios.create({ baseURL: BASE_URL });

// Auto-attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auth ──────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post("/api/auth/register", data),
  login: (data) => api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
};

// ── History ───────────────────────────────────────────────
export const historyAPI = {
  getSessions: () => api.get("/api/history/sessions"),
  getMessages: (sessionId) => api.get(`/api/history/messages/${sessionId}`),
  getMoodSummary: () => api.get("/api/history/mood-summary"),
  getLatestMood: () => api.get("/api/history/latest-mood"),
  getCrisisAlerts: () => api.get("/api/history/crisis-alerts"),
};

// ── WebSocket ─────────────────────────────────────────────
export const createChatSocket = (userId, token, onMessage, onError) => {
  const ws = new WebSocket(`${WS_URL}/ws/chat/${userId}?token=${token}`);

  ws.onopen = () => console.log("✅ WebSocket connected");
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("WS parse error:", e);
    }
  };
  ws.onerror = (e) => {
    console.error("WS error:", e);
    if (onError) onError(e);
  };
  ws.onclose = () => console.log("🔌 WebSocket disconnected");

  return ws;
};

export default api;