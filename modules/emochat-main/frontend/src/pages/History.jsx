// src/pages/History.jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { historyAPI } from "../api/client";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const MOOD_EMOJI = {
  happy: "😊", sad: "😢", anxious: "😰", calm: "😌",
  angry: "😠", hopeless: "😔", lonely: "🥺", overwhelmed: "😵", neutral: "😐"
};

const MOOD_COLOR = {
  happy: "#22c55e", sad: "#60a5fa", anxious: "#f59e0b",
  calm: "#a78bfa", angry: "#ef4444", hopeless: "#6b7280",
  lonely: "#ec4899", overwhelmed: "#f97316", neutral: "#94a3b8"
};

export default function History() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [moodSummary, setMoodSummary] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionMessages, setSessionMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sessRes, moodRes] = await Promise.all([
          historyAPI.getSessions(),
          historyAPI.getMoodSummary()
        ]);
        setSessions(sessRes.data.sessions);
        setMoodSummary(moodRes.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const loadSession = async (sessionId) => {
    try {
      const res = await historyAPI.getMessages(sessionId);
      setSessionMessages(res.data.messages);
      setSelectedSession(sessionId);
    } catch (e) {
      console.error(e);
    }
  };

  // Build chart data from mood history
  const chartData = moodSummary?.history?.slice(0, 20).reverse().map((entry, i) => ({
    name: new Date(entry.timestamp).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    score: Math.round(entry.score * 100),
    mood: entry.mood
  })) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-57px)]">
        <div className="text-center text-gray-400">
          <div className="text-3xl mb-2 animate-pulse">🌿</div>
          <p className="text-sm">Loading your history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">

      {/* Mood Summary */}
      {moodSummary && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Mood Overview</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-indigo-50 rounded-xl p-4 text-center">
              <div className="text-2xl mb-1">
                {MOOD_EMOJI[moodSummary.latest_mood] || "😐"}
              </div>
              <p className="text-xs text-gray-500">Latest Mood</p>
              <p className="text-sm font-semibold text-indigo-700 capitalize">
                {moodSummary.latest_mood}
              </p>
            </div>
            {Object.entries(moodSummary.mood_counts || {}).slice(0, 3).map(([mood, count]) => (
              <div key={mood} className="bg-gray-50 rounded-xl p-4 text-center">
                <div className="text-2xl mb-1">{MOOD_EMOJI[mood]}</div>
                <p className="text-xs text-gray-500 capitalize">{mood}</p>
                <p className="text-sm font-semibold text-gray-700">{count}x</p>
              </div>
            ))}
          </div>

          {/* Mood chart */}
          {chartData.length > 1 && (
            <div>
              <p className="text-sm text-gray-500 mb-3">Mood intensity over time</p>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(val, name) => [`${val}%`, "Intensity"]}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "#6366f1" }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Sessions list + messages */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Sessions */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Past Sessions</h2>
          {sessions.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">No sessions yet</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => loadSession(session.session_id)}
                  className={`w-full text-left p-3 rounded-xl transition text-sm ${
                    selectedSession === session.session_id
                      ? "bg-indigo-50 border border-indigo-200"
                      : "hover:bg-gray-50 border border-transparent"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-700">
                      {MOOD_EMOJI[session.overall_mood] || "😐"} {session.overall_mood}
                    </span>
                    {session.crisis_flagged && (
                      <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full">
                        ⚠️ alert
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400">
                    {new Date(session.started_at).toLocaleDateString("en-IN", {
                      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
                    })}
                  </p>
                  <p className="text-xs text-gray-400">{session.message_count} messages</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="md:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <h2 className="text-base font-semibold text-gray-800 mb-3">
            {selectedSession ? "Session Messages" : "Select a session"}
          </h2>
          {!selectedSession ? (
            <div className="flex items-center justify-center h-48 text-gray-400">
              <p className="text-sm">← Click a session to view messages</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {sessionMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`
                    max-w-xs px-3 py-2 rounded-xl text-sm
                    ${msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-100 text-gray-800"
                    }
                  `}>
                    {msg.content}
                    {msg.mood_detected && msg.role === "bot" && (
                      <p className="text-xs mt-1 opacity-60">
                        {MOOD_EMOJI[msg.mood_detected]} {msg.mood_detected}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Back to chat */}
      <div className="text-center">
        <button
          onClick={() => navigate("/chat")}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Back to chat
        </button>
      </div>
    </div>
  );
}