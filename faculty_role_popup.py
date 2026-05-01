import tkinter as tk
from tkinter import messagebox
import csv
import os
import sys
import json
from datetime import datetime

# File paths
BASE_DIR = r"C:\AttendanceSystem"
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_log.csv")
PENDING_FILE = os.path.join(BASE_DIR, "faculty_pending.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Colors
BG_DARK = "#1B2A4A"
BG_MID  = "#2471A3"
BG_LIGHT = "#AED6F1"
WHITE   = "#FFFFFF"
SUBTLE  = "#85C1E9"
GREEN   = "#27AE60"
RED     = "#C0392B"

# Load config
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

CONFIG = load_config()

ROLES = CONFIG.get('faculty_roles', [
    "Attended Conference",
    "Time in the Vest Lab",
    "Ran a Small Group Session",
    "Lectured in Conference"
]) if CONFIG else [
    "Attended Conference",
    "Time in the Vest Lab",
    "Ran a Small Group Session",
    "Lectured in Conference"
]

# Clear any existing pending file on startup
if os.path.exists(PENDING_FILE):
    os.remove(PENDING_FILE)

def update_roles(target_index, roles_str):
    rows = []
    try:
        with open(ATTENDANCE_FILE, newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for i, row in enumerate(reader):
                if i + 1 == target_index:
                    row['roles'] = roles_str
                rows.append(row)
        with open(ATTENDANCE_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"Error updating roles: {e}")
        return False

class FacultyRoleApp:
    def __init__(self, root, target_index, faculty_name):
        self.root = root
        self.target_index = target_index
        self.faculty_name = faculty_name
        self.responded = False
        self.border_colors = ["#E74C3C", "#F39C12", "#2ECC71", "#3498DB"]
        self.border_index = 0
        self.countdown = 30

        program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
        footer_text = CONFIG.get('branding', {}).get('footer_text', '') if CONFIG else ''

        self.root.title("Faculty Role Selection")
        self.root.geometry("650x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        self.root.lift()
        self.root.attributes('-topmost', True)

        # Header
        header_frame = tk.Frame(self.root, bg=BG_MID, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame,
                text="Faculty Role Selection",
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
        self.blink_border()
        self.check_pending()
        self.update_countdown()

    def build_ui(self):
        # Blinking border frame
        self.border_frame = tk.Frame(self.root, bg="#E74C3C", bd=8, relief="solid")
        self.border_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        inner_frame = tk.Frame(self.border_frame, bg=BG_DARK)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        tk.Label(inner_frame,
                text=f"Welcome, {self.faculty_name}!",
                font=("Arial", 22, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=15)

        tk.Label(inner_frame,
                text="Today I performed the following roles:",
                font=("Arial", 16),
                bg=BG_DARK, fg=SUBTLE).pack(pady=5)

        # Checkboxes
        checkbox_frame = tk.Frame(inner_frame, bg=BG_DARK)
        checkbox_frame.pack(pady=15, padx=30, fill=tk.X)

        self.role_vars = []
        for i, role in enumerate(ROLES):
            var = tk.BooleanVar(value=(i == 0))
            self.role_vars.append(var)
            tk.Checkbutton(checkbox_frame,
                          text=role,
                          variable=var,
                          font=("Arial", 15),
                          bg=BG_DARK, fg=WHITE,
                          selectcolor=BG_MID,
                          activebackground=BG_DARK,
                          activeforeground=WHITE).pack(anchor="w", pady=8)

        self.countdown_label = tk.Label(inner_frame,
                text=f"Auto-submitting in 30 seconds...",
                font=("Arial", 12, "italic"),
                bg=BG_DARK, fg=RED)
        self.countdown_label.pack(pady=5)

        tk.Button(inner_frame,
                 text="Submit",
                 font=("Arial", 18, "bold"),
                 bg=GREEN, fg=WHITE,
                 width=14, height=2,
                 command=self.submit).pack(pady=20)

    def blink_border(self):
        if self.responded:
            return
        color = self.border_colors[self.border_index % len(self.border_colors)]
        self.border_frame.configure(bg=color)
        self.border_index += 1
        self.root.after(500, self.blink_border)

    def update_countdown(self):
        if self.responded:
            return
        if self.countdown <= 0:
            self.auto_submit()
            return
        self.countdown_label.config(
            text=f"Auto-submitting in {self.countdown} seconds...")
        self.countdown -= 1
        self.root.after(1000, self.update_countdown)

    def check_pending(self):
        if self.responded:
            return
        if os.path.exists(PENDING_FILE):
            try:
                os.remove(PENDING_FILE)
            except:
                pass
            self.auto_submit()
            return
        self.root.after(500, self.check_pending)

    def auto_submit(self):
        self.responded = True
        default_role = ROLES[0] if ROLES else "Attended Conference"
        update_roles(self.target_index, default_role)
        self.root.destroy()

    def submit(self):
        self.responded = True
        selected = [ROLES[i] for i, var in enumerate(self.role_vars) if var.get()]
        if not selected:
            selected = [ROLES[0]] if ROLES else ["Attended Conference"]
        roles_str = ", ".join(selected)
        update_roles(self.target_index, roles_str)
        self.root.destroy()

if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: faculty_role_popup.py <target_index> <faculty_name>")
            sys.exit(1)
        target_index = int(sys.argv[1])
        faculty_name = sys.argv[2].replace("_", " ")
        root = tk.Tk()
        app = FacultyRoleApp(root, target_index, faculty_name)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──