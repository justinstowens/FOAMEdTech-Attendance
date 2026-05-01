import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import json
from datetime import datetime

# Load config
BASE_DIR = r"C:\AttendanceSystem"
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

CONFIG = load_config()

def launch_badge_listener(mode):
    subprocess.Popen([
        'python',
        os.path.join(BASE_DIR, 'badge_listener.py'),
        mode
    ])

def select_session(session):
    now = datetime.now()

    if not session.get('tracks_hours', True) and now.hour < 16:
        unusual = messagebox.askyesno(
            "Unusual Time Warning",
            f"It is currently before 4:00 PM.\n\n"
            f"This is an unusual time to start {session['name']}.\n\n"
            f"Are you sure you want to select {session['name'].upper()} mode?"
        )
        if not unusual:
            return

    if session.get('tracks_hours', True):
        session_desc = "Hours will be tracked for this session."
    else:
        log_label = session.get('log_label', session['name'])
        session_desc = f"Attendance will be recorded as '{log_label}' instead of hours."

    confirmed = messagebox.askyesno(
        "Confirm Selection",
        f"You selected {session['name'].upper()} mode.\n\n"
        f"{session_desc}\n\n"
        f"Is this correct?"
    )

    if confirmed:
        root.destroy()
        mode = session['name'].lower().replace(' ', '_')
        launch_badge_listener(mode)

# Build UI
root = tk.Tk()
program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
footer_text = CONFIG.get('branding', {}).get('footer_text', '') if CONFIG else ''
root.title(f"{program_name} — Session Select")
root.resizable(False, False)
root.configure(bg="#1B2A4A")
root.lift()
root.attributes('-topmost', True)

tk.Label(root,
        text="Attendance System",
        font=("Arial", 24, "bold"),
        bg="#1B2A4A", fg="#FFFFFF").pack(pady=15)

tk.Label(root,
        text=program_name,
        font=("Arial", 14),
        bg="#1B2A4A", fg="#AED6F1").pack()

tk.Label(root,
        text="Please select the session type:",
        font=("Arial", 14),
        bg="#1B2A4A", fg="#FFFFFF").pack(pady=5)

tk.Label(root,
        text=f"Current time: {datetime.now().strftime('%I:%M %p')}",
        font=("Arial", 12, "italic"),
        bg="#1B2A4A", fg="#85C1E9").pack(pady=5)

btn_frame = tk.Frame(root, bg="#1B2A4A")
btn_frame.pack(pady=30, padx=40, fill=tk.X)

button_colors = ["#2980B9", "#8E44AD", "#16A085", "#D35400", "#C0392B", "#27AE60"]

if CONFIG and CONFIG.get('session_types'):
    for i, session in enumerate(CONFIG['session_types']):
        color = button_colors[i % len(button_colors)]
        tk.Button(btn_frame,
                 text=session['name'].upper(),
                 font=("Arial", 18, "bold"),
                 bg=color, fg="white",
                 height=3,
                 command=lambda s=session: select_session(s)).pack(fill=tk.X, pady=10)
else:
    tk.Label(btn_frame,
            text="ERROR: Could not load session types from config.json",
            font=("Arial", 12),
            bg="#1B2A4A", fg="#E74C3C").pack(pady=20)

# Branding footer
if footer_text:
    tk.Frame(root, bg="#2471A3", height=2).pack(fill=tk.X, side=tk.BOTTOM)
    tk.Label(root,
            text=footer_text,
            font=("Arial", 8),
            bg="#1B2A4A", fg="#FFFFFF").pack(side=tk.BOTTOM, pady=3)

# Resize window based on number of session types
if CONFIG and CONFIG.get('session_types'):
    num_sessions = len(CONFIG['session_types'])
    window_height = 380 + (num_sessions * 80)
    root.geometry(f"480x{window_height}")

if __name__ == "__main__":
    try:
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──