// src/components/ChatBubble.jsx

const MOOD_EMOJI = {
  happy: "😊", sad: "😢", anxious: "😰", calm: "😌",
  angry: "😠", hopeless: "😔", lonely: "🥺", overwhelmed: "😵", neutral: "😐"
};

export default function ChatBubble({ message }) {
  const isUser = message.role === "user";
  const isOffTopic = message.type === "off_topic";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {/* Bot avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm mr-2 flex-shrink-0 mt-1">
          🌿
        </div>
      )}

      <div className={`max-w-xs lg:max-w-md xl:max-w-lg`}>
        <div className={`
          px-4 py-3 rounded-2xl text-sm leading-relaxed
          ${isUser
            ? "bg-indigo-600 text-white rounded-br-sm"
            : isOffTopic
              ? "bg-amber-50 border border-amber-200 text-amber-800 rounded-bl-sm"
              : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm"
          }
        `}>
          {message.content}
        </div>

        {/* Mood tag on bot messages */}
        {!isUser && message.mood && message.mood !== "neutral" && (
          <div className="flex items-center mt-1 ml-1">
            <span className="text-xs text-gray-400">
              {MOOD_EMOJI[message.mood] || "😐"} {message.mood}
            </span>
          </div>
        )}

        {/* Timestamp */}
        <div className={`text-xs text-gray-400 mt-1 ${isUser ? "text-right" : "text-left ml-1"}`}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit", minute: "2-digit"
          })}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs ml-2 flex-shrink-0 mt-1">
          You
        </div>
      )}
    </div>
  );
}