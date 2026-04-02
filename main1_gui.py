import webview
import subprocess
import threading
import sys
import ctypes
import os

# ✅ Hide console
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ✅ BASE PATH
BASE_DIR = os.path.dirname(__file__)

# ✅ MODULE PATHS (NO RENAME, EXACT SAME)
sys.path.append(os.path.join(BASE_DIR, "modules", "MoodSpotifyPlayer"))
sys.path.append(os.path.join(BASE_DIR, "modules", "Emoheal"))

import voice


class API:

    # ================= CAMERA =================
    def run_facial(self):
        def run_camera():
            try:
                # Emoheal module
                sys.path.append(os.path.join(BASE_DIR, "modules", "Emoheal"))
                import main

                mood = main.run_camera_once()

                if mood:
                    webview.windows[0].evaluate_js(
                        f"updateTreeFromVoice('{mood}')"
                    )

            except Exception as e:
                print("Camera error:", e)

        threading.Thread(target=run_camera).start()

    # ================= VOICE =================
    def run_voice(self):
        import tkinter as tk
        import threading
        import time
        import random
        import voice

        voice_win = tk.Tk()
        voice_win.title("Voice Analysis 🎤")

        width, height = 450, 700
        screen_w = voice_win.winfo_screenwidth()
        screen_h = voice_win.winfo_screenheight()
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        voice_win.geometry(f"{width}x{height}+{x}+{y}")

        voice_win.configure(bg="#f5f6fa")

        tk.Label(voice_win, text="Voice Emotion Detection 🎤",
                 font=("Arial", 18, "bold"),
                 bg="#f5f6fa").pack(pady=10)

        wave_canvas = tk.Canvas(voice_win, width=220, height=80,
                                bg="#f5f6fa", highlightthickness=0)
        wave_canvas.pack()

        bars = []
        for i in range(10):
            bar = wave_canvas.create_rectangle(10 + i*20, 40, 20 + i*20, 40, fill="#6c5ce7")
            bars.append(bar)

        status_label = tk.Label(voice_win, text="Status: Idle",
                                font=("Arial", 12), bg="#f5f6fa")
        status_label.pack(pady=10)

        song_label = tk.Label(voice_win, text="🎵 Song: -",
                              font=("Arial", 11), bg="#f5f6fa")
        song_label.pack()

        tree_label = tk.Label(voice_win, text="🌿 Mood Impact: -",
                              font=("Arial", 11), bg="#f5f6fa")
        tree_label.pack(pady=5)

        bar_frame = tk.Frame(voice_win, bg="#ddd", width=300, height=20)
        bar_frame.pack(pady=10)

        emotion_bar = tk.Frame(bar_frame, bg="#6c5ce7", width=0, height=20)
        emotion_bar.place(x=0, y=0)

        btn_frame = tk.Frame(voice_win, bg="#f5f6fa")
        btn_frame.pack(pady=10)

        running = {"mic": False}

        def animate_wave():
            while running["mic"]:
                for bar in bars:
                    h = random.randint(10, 60)
                    wave_canvas.coords(bar,
                                       wave_canvas.coords(bar)[0], 80-h,
                                       wave_canvas.coords(bar)[2], 80)
                time.sleep(0.1)

        def start_voice():
            running["mic"] = True
            threading.Thread(target=animate_wave, daemon=True).start()

            status_label.config(text="🎤 Listening...")

            def run():
                result = voice.run_voice_once()
                running["mic"] = False

                if isinstance(result, tuple):
                    mood, song = result
                else:
                    mood, song = result, "Unknown"

                status_label.config(text=f"Emotion: {mood}")
                song_label.config(text=f"🎵 {song}")

                value = {
                    "happy": 100,
                    "sad": 40,
                    "angry": 30,
                    "fear": 20,
                    "neutral": 60
                }.get(mood, 10)

                emotion_bar.config(width=value * 3)
                tree_label.config(text=f"🌿 Mood: {mood}")

                try:
                    webview.windows[0].evaluate_js(f"updateTreeFromVoice('{mood}')")
                except:
                    pass

            threading.Thread(target=run).start()

        def detect_again():
            start_voice()

        def stop_voice():
            voice.stop_song()
            running["mic"] = False
            status_label.config(text="⏹ Stopped")

        def resume_voice():
            voice.resume_song()
            status_label.config(text="▶ Resumed")

        def quit_window():
            running["mic"] = False
            voice_win.destroy()

        voice_win.protocol("WM_DELETE_WINDOW", quit_window)

        def btn(text, cmd, color):
            return tk.Button(btn_frame, text=text, command=cmd,
                             width=25, height=2, bg=color,
                             fg="white", font=("Arial", 11, "bold"), bd=0)

        btn("▶ Start", start_voice, "#6c5ce7").pack(pady=5)
        btn("🔁 Detect Again", detect_again, "#0984e3").pack(pady=5)
        btn("⏹ Stop", stop_voice, "#d63031").pack(pady=5)
        btn("⏯ Resume", resume_voice, "#00b894").pack(pady=5)
        btn("❌ Quit", quit_window, "#636e72").pack(pady=10)

        voice_win.mainloop()

    # ================= CHATBOT =================
    def run_chat(self):
        threading.Thread(target=lambda: subprocess.Popen(
            [sys.executable,
             os.path.join(BASE_DIR, "modules", "emochat-main", "backend", "run.py")]
        )).start()

        import time
        time.sleep(2)

        webview.create_window("Chatbot 💬", "http://localhost:8000",
                              width=900, height=700)

    # ================= GAMES =================
    def run_fruit(self):
        subprocess.Popen([
            sys.executable,
            os.path.join(BASE_DIR, "modules", "games",
                         "Fruit_Ninjas_Game-main", "main.py")
        ])

    def run_pacman(self):
        subprocess.Popen([
            sys.executable,
            os.path.join(BASE_DIR, "modules", "games",
                         "pacman-game-main", "pacman.py")
        ])

    # ================= SCORES =================
    def get_latest_score(self):
        from pymongo import MongoClient
        client = MongoClient("mongodb+srv://emoheal_user:Emoheal123@cluster0.hwezm4z.mongodb.net/")
        return client["emohealDB"]["game_data"].find_one(sort=[("timestamp", -1)])["score"]

    def get_latest_pacman_score(self):
        from pymongo import MongoClient
        client = MongoClient("mongodb+srv://emoheal_user:Emoheal123@cluster0.hwezm4z.mongodb.net/")
        return client["emohealDB"]["game_data"].find_one(sort=[("timestamp", -1)])["score"]


# ================= MAIN =================
if __name__ == '__main__':
    api = API()

    def start_server():
        subprocess.Popen(
            ["node", "server/server.js"],
            cwd=BASE_DIR
        )

    threading.Thread(target=start_server).start()

    webview.create_window(
        "EmoHeal 🌿",
        "http://localhost:5000/guest_user.html",
        js_api=api,
        width=1200,
        height=800
    )

    webview.start()