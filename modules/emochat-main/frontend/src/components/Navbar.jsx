// src/components/Navbar.jsx
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      {/* Logo */}
      <Link to="/chat" className="flex items-center gap-2">
        <span className="text-xl">🌿</span>
        <span className="font-bold text-indigo-700 text-lg">EmoHeal</span>
      </Link>

      {/* Nav links */}
      {user && (
        <div className="flex items-center gap-1">
          <Link
            to="/chat"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              isActive("/chat")
                ? "bg-indigo-50 text-indigo-700"
                : "text-gray-600 hover:text-indigo-600 hover:bg-gray-50"
            }`}
          >
            💬 Chat
          </Link>
          <Link
            to="/history"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              isActive("/history")
                ? "bg-indigo-50 text-indigo-700"
                : "text-gray-600 hover:text-indigo-600 hover:bg-gray-50"
            }`}
          >
            📖 History
          </Link>
        </div>
      )}

      {/* User info + logout */}
      {user && (
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">Hi, <span className="font-medium">{user.name}</span></span>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-red-500 transition px-3 py-1.5 rounded-lg hover:bg-red-50"
          >
            Sign out
          </button>
        </div>
      )}
    </nav>
  );
}