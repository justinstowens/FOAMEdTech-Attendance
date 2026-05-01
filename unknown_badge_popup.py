import tkinter as tk
from tkinter import messagebox
import csv
import os
import sys
import json
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_log.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Colors
BG_DARK = "#1B2A4A"
BG_MID  = "#2471A3"
BG_LIGHT = "#AED6F1"
WHITE   = "#FFFFFF"
SUBTLE  = "#85C1E9"
RED     = "#C0392B"

# Timeout in seconds
TIMEOUT = 30

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

CONFIG = load_config()

def log_attendance(badge_id, name, status, subprogram, time_in, hours_credited):
    try:
        file_exists = os.path.exists(ATTENDANCE_FILE)
        with open(ATTENDANCE_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    'date', 'time_in', 'badge_id', 'name',
                    'status', 'grad_year', 'subprogram', 'hours_credited', 'roles'
                ])
            writer.writerow([
                time_in.strftime('%m/%d/%Y'),
                time_in.strftime('%I:%M %p'),
                badge_id,
                name,
                status,
                'N/A',
                subprogram,
                hours_credited,
                ''
            ])
        return True
    except Exception as e:
        print(f"Error logging attendance: {e}")
        return False

class UnknownBadgeApp:
    def __init__(self, root, badge_id, time_in_str, hours_credited):
        self.root = root
        self.badge_id = badge_id
        self.time_in = datetime.strptime(time_in_str, '%Y-%m-%d %H:%M:%S.%f')
        try:
            self.hours_credited = float(hours_credited)
        except ValueError:
            self.hours_credited = hours_credited
        self.countdown = TIMEOUT
        self.responded = False

        program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
        footer_text = CONFIG.get('branding', {}).get('footer_text', '') if CONFIG else ''

        self.root.title("Unrecognized Badge")
        self.root.geometry("520x520")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        self.root.lift()
        self.root.attributes('-topmost', True)

        # Header
        header_frame = tk.Frame(self.root, bg=BG_MID, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame,
                text="Unrecognized Badge",
                font=("Arial", 20, "bold"),
                bg=BG_MID, fg=WHITE).pack(side=tk.LEFT, padx=20)

        tk.Label(header_frame,
                text=program_name,
                font=("Arial", 12),
                bg=BG_MID, fg=BG_LIGHT).pack(side=tk.RIGHT, padx=20)

        # Footer
        if footer_text:
            tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, side=tk.BOTTOM)
            tk.Label(self.root,
                    text=footer_text,
                    font=("Arial", 8),
                    bg=BG_DARK, fg=WHITE).pack(side=tk.BOTTOM, pady=3)

        self.build_ui()
        self.update_countdown()

    def build_ui(self):
        content = tk.Frame(self.root, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(content,
                text="Please identify who you are:",
                font=("Arial", 16, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=10)

        tk.Label(content,
                text=f"Badge ID: {self.badge_id}  |  Time: {self.time_in.strftime('%I:%M %p')}  |  Hours: {self.hours_credited}",
                font=("Arial", 11),
                bg=BG_DARK, fg=SUBTLE).pack(pady=5)

        self.countdown_label = tk.Label(content,
                text=f"Auto-logging in {self.countdown} seconds...",
                font=("Arial", 11, "italic"),
                bg=BG_DARK, fg=RED)
        self.countdown_label.pack(pady=5)

        # Dynamic resident categories from config
        if CONFIG and CONFIG.get('resident_categories'):
            categories = [c for c in CONFIG['resident_categories'] if c.lower() != 'faculty']
            resident_label = ", ".join(categories) + " Resident"
        else:
            resident_label = "EM, EM/IM, or EM/FM Resident"

        btn_frame = tk.Frame(content, bg=BG_DARK)
        btn_frame.pack(pady=10, fill=tk.X)

        buttons = [
            (resident_label, "#2980B9", self.option_resident),
            ("Off-Service Resident", "#8E44AD", self.option_off_service),
            ("Medical Student", "#16A085", self.option_med_student),
            ("Ignore Badge Swipe", "#566573", self.option_ignore),
        ]

        for text, color, command in buttons:
            tk.Button(btn_frame,
                     text=text,
                     font=("Arial", 14, "bold"),
                     bg=color, fg=WHITE,
                     height=2,
                     command=command).pack(fill=tk.X, pady=5)

    def update_countdown(self):
        if self.responded:
            return
        if self.countdown <= 0:
            self.auto_log()
            return
        self.countdown_label.config(
            text=f"Auto-logging as Unknown Resident in {self.countdown} seconds...")
        self.countdown -= 1
        self.root.after(1000, self.update_countdown)

    def auto_log(self):
        log_attendance(
            self.badge_id, "Unknown Resident", "unmatched",
            "Unknown", self.time_in, self.hours_credited
        )
        self.root.destroy()

    def option_resident(self):
        self.responded = True
        log_attendance(
            self.badge_id, "Unknown Resident", "unmatched",
            "Unknown", self.time_in, self.hours_credited
        )
        messagebox.showinfo(
            "Badge Logged",
            "Your badge-in time has been recorded. However, your ID number is not "
            "currently in our system. Please notify a faculty member so your attendance "
            "can be properly assigned to your record and your hours credited accordingly."
        )
        self.root.destroy()

    def option_off_service(self):
        self.responded = True
        log_attendance(
            self.badge_id, "Off-Service Resident", "off_service",
            "Off-Service", self.time_in, self.hours_credited
        )
        self.root.destroy()

    def option_med_student(self):
        self.responded = True
        log_attendance(
            self.badge_id, "Medical Student", "med_student",
            "Medical Student", self.time_in, self.hours_credited
        )
        self.root.destroy()

    def option_ignore(self):
        self.responded = True
        self.root.destroy()

if __name__ == "__main__":
    try:
        if len(sys.argv) != 5:
            print("Usage: unknown_badge_popup.py <badge_id> <date> <time> <hours_credited>")
            sys.exit(1)

        badge_id = sys.argv[1]
        time_in_str = sys.argv[2] + " " + sys.argv[3]
        hours_credited = sys.argv[4]

        root = tk.Tk()
        app = UnknownBadgeApp(root, badge_id, time_in_str, hours_credited)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──
