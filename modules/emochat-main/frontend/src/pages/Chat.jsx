// src/pages/Chat.jsx
import { useState, useEffect, useRef } from "react";
import ChatBubble from "../components/ChatBubble";
import CrisisAlert from "../components/CrisisAlert";

const MOOD_EMOJI = {
  happy: "😊", sad: "😢", anxious: "😰", calm: "😌",
  angry: "😠", hopeless: "😔", lonely: "🥺",
  overwhelmed: "😵", neutral: "😐", distressed: "😰"
};

// WebSocket URL — works both in dev and when served by FastAPI
const WS_URL = `ws://${window.location.hostname}:8000/ws/chat`;

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [typing, setTyping] = useState(false);
  const [crisisAlert, setCrisisAlert] = useState(null);
  const [currentMood, setCurrentMood] = useState("neutral");
  const wsRef = useRef(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Connect WebSocket on mount
  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      console.log("✅ Connected to EmoHeal");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleIncoming(data);
      } catch (e) {
        console.error("Parse error:", e);
      }
    };

    ws.onerror = () => setConnected(false);
    ws.onclose = () => {
      setConnected(false);
      console.log("🔌 Disconnected");
    };

    wsRef.current = ws;
    return () => ws.close();
  }, []);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const handleIncoming = (data) => {
    setTyping(false);

    if (data.type === "crisis_alert") {
      setCrisisAlert(data);
      setMessages((prev) => [...prev, {
        role: "bot",
        content: data.message,
        type: "crisis_alert",
        mood: "distressed",
        timestamp: data.timestamp || new Date().toISOString()
      }]);
      return;
    }

    if (data.type === "bot_response" || data.type === "off_topic" || data.type === "error") {
      if (data.mood) setCurrentMood(data.mood);
      setMessages((prev) => [...prev, {
        role: "bot",
        content: data.message,
        type: data.type,
        mood: data.mood,
        crisis_level: data.crisis_level,
        timestamp: data.timestamp || new Date().toISOString()
      }]);
    }
  };

  const sendMessage = () => {
    const text = input.trim();
    if (!text || !connected || !wsRef.current) return;

    setMessages((prev) => [...prev, {
      role: "user",
      content: text,
      timestamp: new Date().toISOString()
    }]);

    wsRef.current.send(JSON.stringify({ message: text }));
    setInput("");
    setTyping(true);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">

      {/* Crisis Alert Overlay */}
      <CrisisAlert alert={crisisAlert} onDismiss={() => setCrisisAlert(null)} />

      {/* Top bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🌿</span>
          <div>
            <h1 className="font-bold text-indigo-700 text-lg leading-none">EmoHeal</h1>
            <p className="text-xs text-gray-400">Your emotional support companion</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Current mood badge */}
          {currentMood !== "neutral" && (
            <div className="flex items-center gap-1.5 bg-indigo-50 px-3 py-1 rounded-full">
              <span className="text-sm">{MOOD_EMOJI[currentMood]}</span>
              <span className="text-xs text-indigo-700 font-medium capitalize">{currentMood}</span>
            </div>
          )}
          {/* Connection status */}
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-gray-300"}`} />
            <span className="text-xs text-gray-500">{connected ? "Online" : "Connecting..."}</span>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <div className="text-5xl mb-4">🌿</div>
            <p className="text-base font-medium text-gray-500">Welcome to EmoHeal</p>
            <p className="text-sm mt-1">A safe space to share how you're feeling</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatBubble key={i} message={msg} />
        ))}

        {/* Typing indicator */}
        {typing && (
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm flex-shrink-0">
              🌿
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                {[0, 150, 300].map((delay) => (
                  <div
                    key={delay}
                    className="w-2 h-2 bg-indigo-300 rounded-full animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-gray-200 px-4 py-3">
        <div className="flex items-end gap-3 max-w-3xl mx-auto">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Share how you're feeling... (Press Enter to send)"
            rows={1}
            disabled={!connected}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-gray-50 disabled:text-gray-400"
            style={{ minHeight: "44px", maxHeight: "120px" }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || !connected}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-200 text-white rounded-xl px-5 py-2.5 transition font-medium text-sm flex-shrink-0"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          EmoHeal is an AI companion — not a replacement for professional mental health care.
        </p>
      </div>
    </div>
  );
}