// src/components/CrisisAlert.jsx

export default function CrisisAlert({ alert, onDismiss }) {
  if (!alert) return null;

  const isHigh = alert.level === "high";

  return (
    <div className={`
      fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-lg mx-auto px-4
    `}>
      <div className={`
        rounded-2xl shadow-xl p-5 border-2
        ${isHigh
          ? "bg-red-50 border-red-400"
          : "bg-orange-50 border-orange-400"
        }
      `}>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{isHigh ? "🚨" : "⚠️"}</span>
            <div>
              <h3 className={`font-bold text-sm ${isHigh ? "text-red-800" : "text-orange-800"}`}>
                {isHigh ? "You're Not Alone" : "We're Here For You"}
              </h3>
              <p className={`text-xs ${isHigh ? "text-red-600" : "text-orange-600"}`}>
                {isHigh ? "Immediate support available" : "Support is available"}
              </p>
            </div>
          </div>
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Message */}
        {alert.message && (
          <p className={`text-sm mb-4 ${isHigh ? "text-red-700" : "text-orange-700"}`}>
            {alert.message}
          </p>
        )}

        {/* Resources */}
        {alert.resources && (
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Helplines
            </p>
            {Object.entries(alert.resources).map(([name, contact]) => (
              <div key={name} className="flex items-center justify-between bg-white rounded-lg px-3 py-2">
                <span className="text-sm font-medium text-gray-700">{name}</span>
                <span className={`text-sm font-bold ${isHigh ? "text-red-600" : "text-orange-600"}`}>
                  {contact}
                </span>
              </div>
            ))}
          </div>
        )}

        <p className="text-xs text-gray-500 mt-3 text-center">
          Reaching out is a sign of strength 💙
        </p>
      </div>
    </div>
  );
}