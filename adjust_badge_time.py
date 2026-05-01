import tkinter as tk
from tkinter import messagebox
import csv
import os
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
GREEN   = "#1E8449"
RED     = "#C0392B"
BLUE    = "#2980B9"

# Load config
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return None

CONFIG = load_config()

# ── PIN FUNCTIONS ─────────────────────────────────────────────────────────────

def load_pin():
    if not CONFIG:
        return None
    return CONFIG.get('pin', None)

def save_pin(new_pin):
    if not CONFIG:
        return
    CONFIG['pin'] = new_pin
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=4)
    except Exception as e:
        print(f"ERROR saving PIN: {e}")

# ── HOURS CALCULATION ─────────────────────────────────────────────────────────

def calculate_hours_from_time(new_time):
    if not CONFIG:
        return max(0, min(5, 5 - (new_time.hour - 8)))

    session_config = None
    for st in CONFIG.get('session_types', []):
        if st.get('tracks_hours', True):
            session_config = st
            break

    if not session_config:
        return max(0, min(5, 5 - (new_time.hour - 8)))

    start_hour = session_config.get('start_hour', 8)
    total_hours = session_config.get('total_hours', 5)
    credit_method = session_config.get('credit_method', 'full_hour')

    if credit_method == 'full_hour':
        hours = min(total_hours, max(0, total_hours - (new_time.hour - start_hour)))
    elif credit_method == 'exact':
        minutes_late = max(0, (new_time.hour - start_hour) * 60 + new_time.minute)
        hours = max(0, total_hours - minutes_late / 60)
        hours = round(hours, 2)
    elif credit_method == 'half_hour':
        minutes_late = max(0, (new_time.hour - start_hour) * 60 + new_time.minute)
        hours_raw = max(0, total_hours - minutes_late / 60)
        hours = round(hours_raw * 2) / 2
    else:
        hours = min(total_hours, max(0, total_hours - (new_time.hour - start_hour)))

    return round(hours, 1)

# ── ATTENDANCE FUNCTIONS ──────────────────────────────────────────────────────

def load_todays_entries():
    today = datetime.now().strftime('%m/%d/%Y')
    entries = []
    if not os.path.exists(ATTENDANCE_FILE):
        return entries
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row['date'].strip() == today:
                entries.append({'index': i + 1, 'row': row})
    return entries

def update_entry(target_index, new_time_str):
    rows = []
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for i, row in enumerate(reader):
            if i + 1 == target_index:
                new_time = datetime.strptime(new_time_str, '%I:%M %p')
                new_hours = calculate_hours_from_time(new_time)
                row['time_in'] = new_time_str
                row['hours_credited'] = str(new_hours)
            rows.append(row)
    with open(ATTENDANCE_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ── GUI ───────────────────────────────────────────────────────────────────────

class AdjustBadgeApp:
    def __init__(self, root):
        self.root = root
        program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
        footer_text = CONFIG.get('branding', {}).get('footer_text', '') if CONFIG else ''

        self.root.title("Adjust Badge Time")
        self.root.geometry("500x640")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        # Header
        header_frame = tk.Frame(self.root, bg=BG_MID, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame,
                text="Adjust Badge Time",
                font=("Arial", 20, "bold"),
                bg=BG_MID, fg=WHITE).pack(side=tk.LEFT, padx=20)

        tk.Label(header_frame,
                text=program_name,
                font=("Arial", 12),
                bg=BG_MID, fg=BG_LIGHT).pack(side=tk.RIGHT, padx=20)

        # Content area
        self.content = tk.Frame(self.root, bg=BG_DARK)
        self.content.pack(fill=tk.BOTH, expand=True)

        # Footer
        if footer_text:
            tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, side=tk.BOTTOM)
            tk.Label(self.root,
                    text=footer_text,
                    font=("Arial", 8),
                    bg=BG_DARK, fg=WHITE).pack(side=tk.BOTTOM, pady=3)

        self.pin = load_pin()
        self.entered_pin = ""
        self.selected_entry = None

        if self.pin is None:
            self.show_set_pin_screen()
        else:
            self.show_pin_screen()

    def add_numpad(self, parent, press_command):
        pad_frame = tk.Frame(parent, bg=BG_DARK)
        pad_frame.pack(pady=20)

        buttons = [
            ('1', '2', '3'),
            ('4', '5', '6'),
            ('7', '8', '9'),
            ('⌫', '0', '✓')
        ]

        for row in buttons:
            row_frame = tk.Frame(pad_frame, bg=BG_DARK)
            row_frame.pack()
            for btn in row:
                if btn == '✓':
                    color = "#27AE60"
                elif btn == '⌫':
                    color = RED
                else:
                    color = BLUE
                tk.Button(row_frame, text=btn, font=("Arial", 20, "bold"),
                         width=4, height=2, bg=color, fg=WHITE,
                         command=lambda b=btn: press_command(b)).pack(
                         side=tk.LEFT, padx=5, pady=5)

    # ── PIN ENTRY SCREEN ──────────────────────────────────────────────────────

    def show_pin_screen(self):
        self.clear_screen()
        self.entered_pin = ""

        tk.Label(self.content, text="Enter PIN", font=("Arial", 24, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=30)

        self.pin_display = tk.Label(self.content, text="", font=("Arial", 28, "bold"),
                                    bg=BG_DARK, fg=WHITE)
        self.pin_display.pack(pady=10)

        self.add_numpad(self.content, self.pin_button_press)

    def pin_button_press(self, btn):
        if btn == '⌫':
            self.entered_pin = self.entered_pin[:-1]
        elif btn == '✓':
            self.check_pin()
        else:
            self.entered_pin += btn
        try:
            self.pin_display.config(text='●' * len(self.entered_pin))
        except tk.TclError:
            pass

    def check_pin(self):
        if self.entered_pin == self.pin:
            self.show_entries_screen()
        else:
            messagebox.showerror("Incorrect PIN", "That PIN is incorrect. Please try again.")
            self.entered_pin = ""
            self.pin_display.config(text="")

    # ── SET PIN SCREEN ────────────────────────────────────────────────────────

    def show_set_pin_screen(self):
        self.clear_screen()
        self.entered_pin = ""
        self.new_pin = ""

        tk.Label(self.content, text="Set a New PIN", font=("Arial", 24, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=20)
        tk.Label(self.content, text="Enter a PIN to protect\nthe adjustment tool",
                font=("Arial", 14), bg=BG_DARK, fg=SUBTLE).pack(pady=5)

        self.pin_display = tk.Label(self.content, text="", font=("Arial", 28, "bold"),
                                    bg=BG_DARK, fg=WHITE)
        self.pin_display.pack(pady=10)

        self.add_numpad(self.content, self.set_pin_press)

    def set_pin_press(self, btn):
        if btn == '⌫':
            self.entered_pin = self.entered_pin[:-1]
        elif btn == '✓':
            if len(self.entered_pin) < 4:
                messagebox.showwarning("PIN Too Short", "Please enter at least 4 digits.")
                return
            if not self.new_pin:
                self.new_pin = self.entered_pin
                self.entered_pin = ""
                self.pin_display.config(text="")
                messagebox.showinfo("Confirm PIN", "Please enter your PIN again to confirm.")
            else:
                if self.entered_pin == self.new_pin:
                    save_pin(self.new_pin)
                    self.pin = self.new_pin
                    messagebox.showinfo("PIN Set", "PIN has been set successfully!")
                    self.show_entries_screen()
                else:
                    messagebox.showerror("PIN Mismatch", "PINs did not match. Please try again.")
                    self.new_pin = ""
                    self.entered_pin = ""
                    self.pin_display.config(text="")
        else:
            self.entered_pin += btn
        self.pin_display.config(text='●' * len(self.entered_pin))

    # ── ENTRIES SCREEN ────────────────────────────────────────────────────────

    def show_entries_screen(self):
        self.clear_screen()
        self.entries = load_todays_entries()

        tk.Label(self.content, text="Today's Badge Entries",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        if not self.entries:
            tk.Label(self.content, text="No entries found for today.",
                    font=("Arial", 14), bg=BG_DARK, fg=SUBTLE).pack(pady=20)
            tk.Button(self.content, text="Close", font=("Arial", 14, "bold"),
                     bg=RED, fg=WHITE, width=10,
                     command=self.root.destroy).pack(pady=20)
            return

        container = tk.Frame(self.content, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for entry in self.entries:
            row = entry['row']
            btn_text = f"{row['name']}   {row['time_in']}   ({row['hours_credited']} hrs)"
            tk.Button(scroll_frame, text=btn_text, font=("Arial", 13),
                     bg=BLUE, fg=WHITE, anchor="w",
                     command=lambda e=entry: self.show_time_picker(e)).pack(
                     fill=tk.X, pady=4)

        tk.Button(self.content, text="Cancel", font=("Arial", 14, "bold"),
                 bg=RED, fg=WHITE, width=10,
                 command=self.root.destroy).pack(pady=15)

    # ── TIME PICKER SCREEN ────────────────────────────────────────────────────

    def show_time_picker(self, entry):
        self.clear_screen()
        self.selected_entry = entry
        row = entry['row']

        tk.Label(self.content, text="Adjust Time",
                font=("Arial", 20, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=15)
        tk.Label(self.content, text=row['name'],
                font=("Arial", 16), bg=BG_DARK, fg=WHITE).pack()
        tk.Label(self.content, text=f"Current time: {row['time_in']}",
                font=("Arial", 13), bg=BG_DARK, fg=SUBTLE).pack(pady=5)

        time_frame = tk.Frame(self.content, bg=BG_DARK)
        time_frame.pack(pady=20)

        tk.Label(time_frame, text="Hour", font=("Arial", 14),
                bg=BG_DARK, fg=WHITE).grid(row=0, column=0, padx=20)
        tk.Label(time_frame, text="Minute", font=("Arial", 14),
                bg=BG_DARK, fg=WHITE).grid(row=0, column=1, padx=20)
        tk.Label(time_frame, text="AM/PM", font=("Arial", 14),
                bg=BG_DARK, fg=WHITE).grid(row=0, column=2, padx=20)

        self.hour_var = tk.StringVar(value="08")
        self.min_var = tk.StringVar(value="00")
        self.ampm_var = tk.StringVar(value="AM")

        tk.Spinbox(time_frame, from_=1, to=12, textvariable=self.hour_var,
                  font=("Arial", 24, "bold"), width=3, format="%02.0f").grid(
                  row=1, column=0, padx=20)
        tk.Spinbox(time_frame, from_=0, to=59, textvariable=self.min_var,
                  font=("Arial", 24, "bold"), width=3, format="%02.0f").grid(
                  row=1, column=1, padx=20)
        tk.OptionMenu(time_frame, self.ampm_var, "AM", "PM").grid(
                     row=1, column=2, padx=20)

        btn_frame = tk.Frame(self.content, bg=BG_DARK)
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Confirm", font=("Arial", 16, "bold"),
                 bg="#27AE60", fg=WHITE, width=10,
                 command=self.confirm_adjustment).pack(side=tk.LEFT, padx=15)
        tk.Button(btn_frame, text="Cancel", font=("Arial", 16, "bold"),
                 bg=RED, fg=WHITE, width=10,
                 command=self.show_entries_screen).pack(side=tk.LEFT, padx=15)

    def confirm_adjustment(self):
        hour = self.hour_var.get().zfill(2)
        minute = self.min_var.get().zfill(2)
        ampm = self.ampm_var.get()
        new_time_str = f"{hour}:{minute} {ampm}"

        row = self.selected_entry['row']
        new_time = datetime.strptime(new_time_str, '%I:%M %p')
        new_hours = calculate_hours_from_time(new_time)

        confirm = messagebox.askyesno(
            "Confirm Adjustment",
            f"Change {row['name']}\n"
            f"From: {row['time_in']} ({row['hours_credited']} hrs)\n"
            f"To: {new_time_str} ({new_hours} hrs)?\n"
        )

        if confirm:
            update_entry(self.selected_entry['index'], new_time_str)
            messagebox.showinfo("Success",
                f"{row['name']} updated to {new_time_str} ({new_hours} hrs)")
            self.root.destroy()

    # ── UTILITY ───────────────────────────────────────────────────────────────

    def clear_screen(self):
        for widget in self.content.winfo_children():
            widget.destroy()

# Run the app
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.lift()
        root.attributes('-topmost', True)
        app = AdjustBadgeApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──
