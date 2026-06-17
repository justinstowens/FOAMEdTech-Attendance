import keyboard
import csv
import os
import winsound
import subprocess
import shutil
import sys
import json
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
from threading import Thread

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROSTER_FILE = os.path.join(BASE_DIR, "roster.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_log.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Load config
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ERROR loading config: {e}")
        return None

CONFIG = load_config()

# Colors
BG_DARK     = "#1B2A4A"
BG_MID      = "#2471A3"
BG_LIGHT    = "#AED6F1"
GREEN       = "#FFFFFF"
RED         = "#C0392B"
WHITE       = "#FFFFFF"
SUBTLE      = "#85C1E9"
GREY        = "#566573"
YELLOW      = "#D4AC0D"

# Beep functions
def beep_success():
    winsound.Beep(1000, 800)

def beep_unknown():
    winsound.Beep(400, 800)
    winsound.Beep(400, 800)

def beep_error():
    winsound.Beep(600, 800)
    winsound.Beep(600, 800)
    winsound.Beep(600, 800)

def beep_duplicate():
    winsound.Beep(1000, 400)
    winsound.Beep(1000, 400)

def beep_faculty():
    winsound.Beep(1000, 800)
    winsound.Beep(1000, 800)

# Load roster into memory
def load_roster():
    roster = {}
    try:
        with open(ROSTER_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                roster[row['badge_id'].strip()] = {
                    'name': row['name'].strip(),
                    'status': row['status'].strip(),
                    'grad_year': row['grad_year'].strip(),
                    'subprogram': row['subprogram'].strip()
                }
    except Exception as e:
        pass
    return roster

# Calculate hours credited based on badge-in time
def calculate_hours(time_in, session_config):
    hour = time_in.hour
    start_hour = session_config.get('start_hour', 8)
    total_hours = session_config.get('total_hours', 5)
    credit_method = session_config.get('credit_method', 'full_hour')

    if credit_method == 'full_hour':
        hours_credited = min(total_hours, max(0, total_hours - (hour - start_hour)))
    elif credit_method == 'exact':
        minutes_late = max(0, (hour - start_hour) * 60 + time_in.minute)
        hours_credited = max(0, total_hours - minutes_late / 60)
        hours_credited = round(hours_credited, 2)
    elif credit_method == 'half_hour':
        minutes_late = max(0, (hour - start_hour) * 60 + time_in.minute)
        hours_raw = max(0, total_hours - minutes_late / 60)
        hours_credited = round(hours_raw * 2) / 2
    else:
        hours_credited = min(total_hours, max(0, total_hours - (hour - start_hour)))

    return round(hours_credited, 1)

def already_badged_today(badge_id):
    today = datetime.now().strftime('%m/%d/%Y')
    if not os.path.exists(ATTENDANCE_FILE):
        return False
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['badge_id'].strip() == badge_id and row['date'].strip() == today:
                return True
    return False

def get_next_row_index():
    if not os.path.exists(ATTENDANCE_FILE):
        return 1
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.reader(f)
        return sum(1 for row in reader) - 1

def log_attendance(badge_id, learner, time_in, hours_credited):
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
                learner['name'],
                learner['status'],
                learner['grad_year'],
                learner['subprogram'],
                hours_credited,
                ''
            ])
        return True
    except Exception as e:
        return False

def backup_attendance_log():
    if not os.path.exists(ATTENDANCE_FILE):
        return
    backup_dir = os.path.join(BASE_DIR, "Backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"attendance_log_backup_{timestamp}.csv")
    shutil.copy2(ATTENDANCE_FILE, backup_path)

# ── GUI ───────────────────────────────────────────────────────────────────────

class BadgeListenerApp:
    def __init__(self, root, mode, session_config, tracks_hours, faculty_roles_enabled, log_label, badge_id_length, roster):
        self.root = root
        self.mode = mode
        self.session_config = session_config
        self.tracks_hours = tracks_hours
        self.faculty_roles_enabled = faculty_roles_enabled
        self.log_label = log_label
        self.badge_id_length = badge_id_length
        self.roster = roster
        self.resident_count = 0
        self.faculty_count = 0
        self.todays_swipes = set()
        self.current_input = ""

        # Full screen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_DARK)
        self.root.title("Attendance System")

        # Allow Escape to exit fullscreen for emergencies
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))

        self.build_ui()
        self.update_clock()
        self.start_listener()

    def build_ui(self):
        program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
        footer_text = CONFIG.get('branding', {}).get('footer_text', '') if CONFIG else ''

        # ── Header ──
        header_frame = tk.Frame(self.root, bg=BG_MID, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame,
                text="Attendance System",
                font=("Arial", 28, "bold"),
                bg=BG_MID, fg=WHITE).pack(side=tk.LEFT, padx=20)

        tk.Label(header_frame,
                text=program_name,
                font=("Arial", 16),
                bg=BG_MID, fg=BG_LIGHT).pack(side=tk.LEFT, padx=10)

        self.mode_label = tk.Label(header_frame,
                text=f"MODE: {self.mode.upper()}",
                font=("Arial", 16, "bold"),
                bg=BG_MID, fg=YELLOW)
        self.mode_label.pack(side=tk.RIGHT, padx=20)

        self.clock_label = tk.Label(header_frame,
                text="",
                font=("Arial", 16),
                bg=BG_MID, fg=WHITE)
        self.clock_label.pack(side=tk.RIGHT, padx=20)

        # ── Column headers ──
        col_frame = tk.Frame(self.root, bg=BG_DARK, pady=5)
        col_frame.pack(fill=tk.X, padx=20)

        tk.Label(col_frame, text=f"{'Time':<12} {'Name':<30} {'Program':<12} {'Hours':<10} {'Status'}",
                font=("Arial", 13, "bold"),
                bg=BG_DARK, fg=SUBTLE).pack(anchor="w")

        tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, padx=20)

        # ── Scrollable log area ──
        log_container = tk.Frame(self.root, bg=BG_DARK)
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(log_container, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(log_container, orient="vertical", command=self.canvas.yview)
        self.log_frame = tk.Frame(self.canvas, bg=BG_DARK)

        self.log_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.log_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Counter bar ──
        tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, padx=20)

        counter_frame = tk.Frame(self.root, bg=BG_DARK, pady=8)
        counter_frame.pack(fill=tk.X, padx=20)

        self.counter_label = tk.Label(counter_frame,
                text="Residents: 0   |   Faculty: 0",
                font=("Arial", 14, "bold"),
                bg=BG_DARK, fg=WHITE)
        self.counter_label.pack(side=tk.LEFT)

        tk.Button(counter_frame,
                 text="End Session",
                 font=("Arial", 12, "bold"),
                 bg=RED, fg=WHITE,
                 width=12,
                 command=self.end_session).pack(side=tk.RIGHT)

        # ── Footer ──
        tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X)

        footer_frame = tk.Frame(self.root, bg=BG_DARK, pady=4)
        footer_frame.pack(fill=tk.X)

        tk.Label(footer_frame,
                text=footer_text,
                font=("Arial", 8),
                bg=BG_DARK, fg="#566573").pack(side=tk.LEFT, padx=10)

    def add_log_entry(self, time_str, name, subprogram, hours, status, color):
        row_text = f"{time_str:<12} {name:<30} {subprogram:<12} {str(hours):<10} {status}"
        tk.Label(self.log_frame,
                text=row_text,
                font=("Arial", 13),
                bg=BG_DARK, fg=color,
                anchor="w").pack(fill=tk.X, pady=1)

        # Auto scroll to bottom
        self.root.after(100, lambda: self.canvas.yview_moveto(1.0))

    def update_counter(self):
        self.counter_label.config(
            text=f"Residents: {self.resident_count}   |   Faculty: {self.faculty_count}"
        )

    def end_session(self):
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "End Session",
            "Are you sure you want to end the session?\n\nThis will close the badge listener."
        )
        if confirm:
            self.root.destroy()

    def update_clock(self):
        self.clock_label.config(text=datetime.now().strftime('%I:%M %p'))
        self.root.after(1000, self.update_clock)

    def _clear_input_buffer(self):
        if self.current_input:
            beep_unknown()
            self.root.after(0, lambda: self.add_log_entry(
                datetime.now().strftime('%I:%M %p'),
                'Invalid badge format', '', '',
                '⚠ Ignored',
                YELLOW
            ))
        self.current_input = ""
        self._clear_timer = None

    def start_listener(self):
        thread = Thread(target=self.run_listener, daemon=True)
        thread.start()

    def run_listener(self):
        def on_key_event(event):
            if event.event_type != 'down':
                return

            if event.name.isdigit():
                # Cancel any existing timeout
                if hasattr(self, '_clear_timer') and self._clear_timer:
                    self._clear_timer.cancel()

                self.current_input += event.name

                # If too many digits, clear immediately
                if len(self.current_input) > self.badge_id_length:
                    self.current_input = ""
                    self._clear_timer = None
                    beep_unknown()
                    self.root.after(0, lambda: self.add_log_entry(
                        datetime.now().strftime('%I:%M %p'),
                        'Invalid badge format', '', '',
                        '⚠ Ignored',
                        YELLOW
                    ))
                    return

                # Set a timeout to clear buffer if no more digits arrive
                import threading
                self._clear_timer = threading.Timer(0.5, self._clear_input_buffer)
                self._clear_timer.start()

                if len(self.current_input) == self.badge_id_length:
                    # Cancel the timeout since we have a complete ID
                    if self._clear_timer:
                        self._clear_timer.cancel()
                        self._clear_timer = None
                    badge_id = self.current_input
                    self.current_input = ""
                    time_in = datetime.now()

                    if badge_id in self.roster:
                        learner = self.roster[badge_id]
                        today_key = f"{badge_id}_{time_in.strftime('%m/%d/%Y')}"

                        if today_key in self.todays_swipes or already_badged_today(badge_id):
                            beep_duplicate()
                            self.root.after(0, lambda: self.add_log_entry(
                                time_in.strftime('%I:%M %p'),
                                learner['name'],
                                learner['subprogram'],
                                '',
                                '↩ Duplicate',
                                GREY
                            ))
                        else:
                            if not self.tracks_hours:
                                hours_credited = self.log_label if self.log_label else self.mode
                            else:
                                hours_credited = calculate_hours(time_in, self.session_config)

                            success = log_attendance(badge_id, learner, time_in, hours_credited)

                            if success:
                                self.todays_swipes.add(today_key)

                                if learner['subprogram'] == 'Faculty':
                                    beep_faculty()
                                    self.faculty_count += 1
                                else:
                                    beep_success()
                                    self.resident_count += 1

                                self.root.after(0, lambda n=learner['name'], sp=learner['subprogram'], h=hours_credited: self.add_log_entry(
                                    time_in.strftime('%I:%M %p'),
                                    n, sp, h,
                                    '✓ Logged',
                                    GREEN
                                ))
                                self.root.after(0, self.update_counter)

                                if learner['subprogram'] == 'Faculty' and self.faculty_roles_enabled:
                                    next_row = get_next_row_index()
                                    with open(os.path.join(BASE_DIR, 'faculty_pending.txt'), 'w') as fp:
                                        fp.write('close')
                                    subprocess.Popen([
                                        'python',
                                        os.path.join(BASE_DIR, 'faculty_role_popup.py'),
                                        str(next_row),
                                        learner['name'].replace(' ', '_')
                                    ])
                                else:
                                    with open(os.path.join(BASE_DIR, 'faculty_pending.txt'), 'w') as fp:
                                        fp.write('close')
                            else:
                                beep_error()
                                self.root.after(0, lambda: self.add_log_entry(
                                    time_in.strftime('%I:%M %p'),
                                    badge_id, '', '',
                                    '✗ Error',
                                    RED
                                ))
                    else:
                        hours_credited = calculate_hours(time_in, self.session_config) if self.tracks_hours else (self.log_label if self.log_label else self.mode)
                        beep_unknown()
                        self.root.after(0, lambda: self.add_log_entry(
                            time_in.strftime('%I:%M %p'),
                            f'Unknown: {badge_id}', '', '',
                            '? Unknown',
                            YELLOW
                        ))
                        subprocess.Popen([
                            'python',
                            os.path.join(BASE_DIR, 'unknown_badge_popup.py'),
                            badge_id,
                            str(time_in.date()),
                            str(time_in.time()),
                            str(hours_credited)
                        ])

        keyboard.hook(on_key_event)
        keyboard.wait('ctrl+c')

def main():
    if not CONFIG:
        print("ERROR: Could not load config.json!")
        input("Press Enter to close...")
        return

    backup_attendance_log()

    # Get mode from command line argument
    mode = sys.argv[1] if len(sys.argv) > 1 else CONFIG['session_types'][0]['name'].lower().replace(' ', '_')

    # Find matching session config
    session_config = None
    for st in CONFIG['session_types']:
        if st['name'].lower().replace(' ', '_') == mode:
            session_config = st
            break
    if not session_config:
        session_config = CONFIG['session_types'][0]

    tracks_hours = session_config.get('tracks_hours', True)
    faculty_roles = session_config.get('faculty_roles', True)
    log_label = session_config.get('log_label', None)
    badge_id_length = CONFIG.get('badge_id_length', 9)

    roster = load_roster()

    root = tk.Tk()
    app = BadgeListenerApp(
        root,
        session_config['name'],
        session_config,
        tracks_hours,
        faculty_roles,
        log_label,
        badge_id_length,
        roster
    )
    root.mainloop()

if __name__ == "__main__":
    main()
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──
