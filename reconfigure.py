import tkinter as tk
from tkinter import messagebox
import json
import os
import copy

# File paths
BASE_DIR = r"C:\AttendanceSystem"
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Colors
BG_DARK  = "#1B2A4A"
BG_MID   = "#2471A3"
BG_LIGHT = "#AED6F1"
WHITE    = "#FFFFFF"
SUBTLE   = "#85C1E9"
GREEN    = "#27AE60"
RED      = "#C0392B"
BLUE     = "#2980B9"
YELLOW   = "#F39C12"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load config.json:\n{e}")
        return None

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config.json:\n{e}")
        return False

class ReconfigureApp:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        if not self.config:
            self.root.destroy()
            return

        # Work on a deep copy so changes can be cancelled
        self.working_config = copy.deepcopy(self.config)
        self.entered_pin = ""

        program_name = self.config.get('program_name', 'Attendance System')
        self.root.title(f"Reconfigure — {program_name}")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        self.root.lift()
        self.root.attributes('-topmost', True)

        self.build_header()
        self.content = tk.Frame(self.root, bg=BG_DARK)
        self.content.pack(fill=tk.BOTH, expand=True)
        self.build_footer()

        self.show_pin_screen()

    def build_header(self):
        header_frame = tk.Frame(self.root, bg=BG_MID, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame,
                text="System Reconfiguration",
                font=("Arial", 20, "bold"),
                bg=BG_MID, fg=WHITE).pack(side=tk.LEFT, padx=20)

        program_name = self.config.get('program_name', 'Attendance System')
        tk.Label(header_frame,
                text=program_name,
                font=("Arial", 12),
                bg=BG_MID, fg=BG_LIGHT).pack(side=tk.RIGHT, padx=20)

    def build_footer(self):
        footer_text = self.config.get('branding', {}).get('footer_text', '')
        if footer_text:
            tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, side=tk.BOTTOM)
            tk.Label(self.root,
                    text=footer_text,
                    font=("Arial", 8),
                    bg=BG_DARK, fg=WHITE).pack(side=tk.BOTTOM, pady=3)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

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
                    color = GREEN
                elif btn == '⌫':
                    color = RED
                else:
                    color = BLUE
                tk.Button(row_frame, text=btn, font=("Arial", 20, "bold"),
                         width=4, height=2, bg=color, fg=WHITE,
                         command=lambda b=btn: press_command(b)).pack(
                         side=tk.LEFT, padx=5, pady=5)

    # ── PIN SCREEN ────────────────────────────────────────────────────────────

    def show_pin_screen(self):
        self.clear_content()
        self.entered_pin = ""

        tk.Label(self.content, text="Enter PIN to Continue",
                font=("Arial", 20, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=25)

        self.pin_display = tk.Label(self.content, text="",
                font=("Arial", 28, "bold"), bg=BG_DARK, fg=WHITE)
        self.pin_display.pack(pady=10)

        self.add_numpad(self.content, self.pin_press)

    def pin_press(self, btn):
        if btn == '⌫':
            self.entered_pin = self.entered_pin[:-1]
        elif btn == '✓':
            stored_pin = self.config.get('pin')
            if self.entered_pin == stored_pin:
                self.show_main_menu()
            else:
                messagebox.showerror("Incorrect PIN", "That PIN is incorrect.")
                self.entered_pin = ""
                self.pin_display.config(text="")
                return
        else:
            self.entered_pin += btn
        try:
            self.pin_display.config(text='●' * len(self.entered_pin))
        except tk.TclError:
            pass

    # ── MAIN MENU ─────────────────────────────────────────────────────────────

    def show_main_menu(self):
        self.clear_content()

        tk.Label(self.content, text="What would you like to change?",
                font=("Arial", 16), bg=BG_DARK, fg=SUBTLE).pack(pady=20)

        menu_items = [
            ("Program Settings", BLUE, self.show_program_settings),
            ("Session Types", BLUE, self.show_session_types),
            ("Resident Categories", BLUE, self.show_resident_categories),
            ("Faculty Roles", BLUE, self.show_faculty_roles),
            ("Change PIN", BLUE, self.show_change_pin),
        ]

        btn_frame = tk.Frame(self.content, bg=BG_DARK)
        btn_frame.pack(pady=10, padx=40, fill=tk.X)

        for text, color, command in menu_items:
            tk.Button(btn_frame, text=text,
                     font=("Arial", 15, "bold"),
                     bg=color, fg=WHITE,
                     height=2,
                     command=command).pack(fill=tk.X, pady=6)

        tk.Button(btn_frame, text="Save & Exit",
                 font=("Arial", 15, "bold"),
                 bg=GREEN, fg=WHITE,
                 height=2,
                 command=self.save_and_exit).pack(fill=tk.X, pady=6)

        tk.Button(btn_frame, text="Cancel (no changes saved)",
                 font=("Arial", 12),
                 bg=RED, fg=WHITE,
                 height=1,
                 command=self.root.destroy).pack(fill=tk.X, pady=6)

    # ── PROGRAM SETTINGS ──────────────────────────────────────────────────────

    def show_program_settings(self):
        self.clear_content()

        tk.Label(self.content, text="Program Settings",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(padx=40, fill=tk.X)

        # Program name
        tk.Label(form, text="Program Name:",
                font=("Arial", 13), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(10,2))
        self.prog_name_var = tk.StringVar(value=self.working_config.get('program_name', ''))
        tk.Entry(form, textvariable=self.prog_name_var,
                font=("Arial", 13), width=40).pack(anchor="w")

        # Badge ID length
        tk.Label(form, text="Badge ID Length (number of digits):",
                font=("Arial", 13), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(15,2))
        self.badge_len_var = tk.StringVar(value=str(self.working_config.get('badge_id_length', 9)))
        tk.Spinbox(form, from_=4, to=20, textvariable=self.badge_len_var,
                  font=("Arial", 13), width=5).pack(anchor="w")

        btn_frame = tk.Frame(self.content, bg=BG_DARK)
        btn_frame.pack(pady=30, padx=40, fill=tk.X)

        tk.Button(btn_frame, text="Save Changes",
                 font=("Arial", 14, "bold"),
                 bg=GREEN, fg=WHITE, width=15,
                 command=self.save_program_settings).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Back",
                 font=("Arial", 14, "bold"),
                 bg=BLUE, fg=WHITE, width=10,
                 command=self.show_main_menu).pack(side=tk.LEFT, padx=5)

    def save_program_settings(self):
        name = self.prog_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Info", "Program name cannot be empty.")
            return
        try:
            badge_len = int(self.badge_len_var.get())
            if badge_len < 4 or badge_len > 20:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Input", "Badge ID length must be between 4 and 20.")
            return

        self.working_config['program_name'] = name
        self.working_config['badge_id_length'] = badge_len
        messagebox.showinfo("Saved", "Program settings updated.\nRemember to click Save & Exit to write changes.")
        self.show_main_menu()

    # ── SESSION TYPES ─────────────────────────────────────────────────────────

    def show_session_types(self):
        self.clear_content()

        tk.Label(self.content, text="Session Types",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        sessions = self.working_config.get('session_types', [])

        list_frame = tk.Frame(self.content, bg=BG_DARK)
        list_frame.pack(padx=40, fill=tk.X)

        for i, session in enumerate(sessions):
            row = tk.Frame(list_frame, bg=BG_DARK)
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=session['name'],
                    font=("Arial", 13), bg=BG_DARK, fg=WHITE,
                    width=20, anchor="w").pack(side=tk.LEFT)

            tracks = "Tracks Hours" if session.get('tracks_hours', True) else "No Hours"
            tk.Label(row, text=tracks,
                    font=("Arial", 11), bg=BG_DARK, fg=SUBTLE).pack(side=tk.LEFT, padx=10)

            tk.Button(row, text="Edit", font=("Arial", 11),
                     bg=BLUE, fg=WHITE,
                     command=lambda s=session, idx=i: self.edit_session(s, idx)).pack(side=tk.LEFT, padx=5)

            tk.Button(row, text="Remove", font=("Arial", 11),
                     bg=RED, fg=WHITE,
                     command=lambda idx=i: self.remove_session(idx)).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.content, bg=BG_DARK)
        btn_frame.pack(pady=20, padx=40, fill=tk.X)

        tk.Button(btn_frame, text="Add New Session Type",
                 font=("Arial", 13, "bold"),
                 bg=GREEN, fg=WHITE,
                 command=lambda: self.edit_session(None, None)).pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Back",
                 font=("Arial", 13, "bold"),
                 bg=BLUE, fg=WHITE,
                 command=self.show_main_menu).pack(fill=tk.X, pady=5)

    def edit_session(self, session, index):
        self.clear_content()

        is_new = session is None
        session = session or {
            'name': '',
            'tracks_hours': True,
            'start_hour': 8,
            'total_hours': 5,
            'credit_method': 'full_hour',
            'faculty_roles': True,
            'log_label': ''
        }

        tk.Label(self.content,
                text="Add Session Type" if is_new else "Edit Session Type",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=15)

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(padx=40, fill=tk.X)

        # Name
        tk.Label(form, text="Session Name:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(8,2))
        name_var = tk.StringVar(value=session.get('name', ''))
        tk.Entry(form, textvariable=name_var, font=("Arial", 12), width=30).pack(anchor="w")

        # Tracks hours
        tracks_var = tk.BooleanVar(value=session.get('tracks_hours', True))
        tk.Checkbutton(form, text="Track hours for this session",
                      variable=tracks_var, font=("Arial", 12),
                      bg=BG_DARK, fg=WHITE, selectcolor=BG_MID,
                      activebackground=BG_DARK, activeforeground=WHITE).pack(anchor="w", pady=8)

        # Start hour
        tk.Label(form, text="Start Hour (24hr, e.g. 8 for 8am):", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(8,2))
        start_var = tk.StringVar(value=str(session.get('start_hour', 8)))
        tk.Spinbox(form, from_=0, to=23, textvariable=start_var, font=("Arial", 12), width=5).pack(anchor="w")

        # Total hours
        tk.Label(form, text="Total Hours Available:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(8,2))
        hours_var = tk.StringVar(value=str(session.get('total_hours', 5)))
        tk.Spinbox(form, from_=1, to=12, textvariable=hours_var, font=("Arial", 12), width=5).pack(anchor="w")

        # Credit method
        tk.Label(form, text="Credit Method:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(8,2))
        credit_var = tk.StringVar(value=session.get('credit_method', 'full_hour'))
        credit_options = [
            ("Full hour credit for partial attendance (Standard)", "full_hour"),
            ("Exact hours based on badge-in time to the minute", "exact"),
            ("Round to nearest half hour", "half_hour")
        ]
        for label, value in credit_options:
            tk.Radiobutton(form, text=label, variable=credit_var, value=value,
                          font=("Arial", 11), bg=BG_DARK, fg=WHITE,
                          selectcolor=BG_MID, activebackground=BG_DARK,
                          activeforeground=WHITE).pack(anchor="w")

        # Faculty roles
        faculty_var = tk.BooleanVar(value=session.get('faculty_roles', True))
        tk.Checkbutton(form, text="Show faculty role popup for this session",
                      variable=faculty_var, font=("Arial", 12),
                      bg=BG_DARK, fg=WHITE, selectcolor=BG_MID,
                      activebackground=BG_DARK, activeforeground=WHITE).pack(anchor="w", pady=8)

        # Log label
        tk.Label(form, text="Log Label (if not tracking hours, e.g. 'Journal Club'):",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(8,2))
        log_label_var = tk.StringVar(value=session.get('log_label', '') or '')
        tk.Entry(form, textvariable=log_label_var, font=("Arial", 12), width=30).pack(anchor="w")

        def save_session():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Missing Info", "Session name cannot be empty.")
                return
            try:
                start_hour = int(start_var.get())
                total_hours = int(hours_var.get())
            except ValueError:
                messagebox.showwarning("Invalid Input", "Start hour and total hours must be numbers.")
                return

            updated = {
                'name': name,
                'tracks_hours': tracks_var.get(),
                'start_hour': start_hour,
                'total_hours': total_hours,
                'credit_method': credit_var.get(),
                'faculty_roles': faculty_var.get(),
                'log_label': log_label_var.get().strip() or None
            }

            if is_new:
                self.working_config['session_types'].append(updated)
            else:
                self.working_config['session_types'][index] = updated

            messagebox.showinfo("Saved", "Session type updated.")
            self.show_session_types()

        btn_frame = tk.Frame(self.content, bg=BG_DARK)
        btn_frame.pack(pady=15, padx=40, fill=tk.X)

        tk.Button(btn_frame, text="Save", font=("Arial", 13, "bold"),
                 bg=GREEN, fg=WHITE, width=12,
                 command=save_session).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Cancel", font=("Arial", 13, "bold"),
                 bg=RED, fg=WHITE, width=12,
                 command=self.show_session_types).pack(side=tk.LEFT, padx=5)

    def remove_session(self, index):
        sessions = self.working_config.get('session_types', [])
        if len(sessions) <= 1:
            messagebox.showwarning("Cannot Remove", "You must have at least one session type.")
            return
        name = sessions[index]['name']
        confirm = messagebox.askyesno("Confirm", f"Remove session type '{name}'?")
        if confirm:
            self.working_config['session_types'].pop(index)
            self.show_session_types()

    # ── RESIDENT CATEGORIES ───────────────────────────────────────────────────

    def show_resident_categories(self):
        self.clear_content()

        tk.Label(self.content, text="Resident Categories",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        categories = self.working_config.get('resident_categories', [])

        list_frame = tk.Frame(self.content, bg=BG_DARK)
        list_frame.pack(padx=40, fill=tk.X)

        for i, cat in enumerate(categories):
            row = tk.Frame(list_frame, bg=BG_DARK)
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=cat, font=("Arial", 13),
                    bg=BG_DARK, fg=WHITE, width=25, anchor="w").pack(side=tk.LEFT)

            tk.Button(row, text="Remove", font=("Arial", 11),
                     bg=RED, fg=WHITE,
                     command=lambda idx=i: self.remove_category(idx)).pack(side=tk.LEFT, padx=5)

        # Add new
        add_frame = tk.Frame(self.content, bg=BG_DARK)
        add_frame.pack(padx=40, pady=20, fill=tk.X)

        tk.Label(add_frame, text="Add new category:",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w")

        self.new_cat_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.new_cat_var,
                font=("Arial", 12), width=25).pack(side=tk.LEFT, pady=5)

        tk.Button(add_frame, text="Add", font=("Arial", 12, "bold"),
                 bg=GREEN, fg=WHITE,
                 command=self.add_category).pack(side=tk.LEFT, padx=10)

        tk.Button(self.content, text="Back", font=("Arial", 13, "bold"),
                 bg=BLUE, fg=WHITE, width=15,
                 command=self.show_main_menu).pack(pady=10)

    def add_category(self):
        new_cat = self.new_cat_var.get().strip()
        if not new_cat:
            messagebox.showwarning("Missing Info", "Please enter a category name.")
            return
        if new_cat in self.working_config.get('resident_categories', []):
            messagebox.showwarning("Duplicate", "That category already exists.")
            return
        self.working_config['resident_categories'].append(new_cat)
        self.show_resident_categories()

    def remove_category(self, index):
        categories = self.working_config.get('resident_categories', [])
        if len(categories) <= 1:
            messagebox.showwarning("Cannot Remove", "You must have at least one category.")
            return
        name = categories[index]
        confirm = messagebox.askyesno("Confirm", f"Remove category '{name}'?")
        if confirm:
            self.working_config['resident_categories'].pop(index)
            self.show_resident_categories()

    # ── FACULTY ROLES ─────────────────────────────────────────────────────────

    def show_faculty_roles(self):
        self.clear_content()

        tk.Label(self.content, text="Faculty Roles",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        roles = self.working_config.get('faculty_roles', [])

        list_frame = tk.Frame(self.content, bg=BG_DARK)
        list_frame.pack(padx=40, fill=tk.X)

        for i, role in enumerate(roles):
            row = tk.Frame(list_frame, bg=BG_DARK)
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=role, font=("Arial", 13),
                    bg=BG_DARK, fg=WHITE, width=35, anchor="w").pack(side=tk.LEFT)

            tk.Button(row, text="Remove", font=("Arial", 11),
                     bg=RED, fg=WHITE,
                     command=lambda idx=i: self.remove_role(idx)).pack(side=tk.LEFT, padx=5)

        add_frame = tk.Frame(self.content, bg=BG_DARK)
        add_frame.pack(padx=40, pady=20, fill=tk.X)

        tk.Label(add_frame, text="Add new role:",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w")

        self.new_role_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.new_role_var,
                font=("Arial", 12), width=35).pack(side=tk.LEFT, pady=5)

        tk.Button(add_frame, text="Add", font=("Arial", 12, "bold"),
                 bg=GREEN, fg=WHITE,
                 command=self.add_role).pack(side=tk.LEFT, padx=10)

        tk.Button(self.content, text="Back", font=("Arial", 13, "bold"),
                 bg=BLUE, fg=WHITE, width=15,
                 command=self.show_main_menu).pack(pady=10)

    def add_role(self):
        new_role = self.new_role_var.get().strip()
        if not new_role:
            messagebox.showwarning("Missing Info", "Please enter a role name.")
            return
        if new_role in self.working_config.get('faculty_roles', []):
            messagebox.showwarning("Duplicate", "That role already exists.")
            return
        self.working_config['faculty_roles'].append(new_role)
        self.show_faculty_roles()

    def remove_role(self, index):
        roles = self.working_config.get('faculty_roles', [])
        if len(roles) <= 1:
            messagebox.showwarning("Cannot Remove", "You must have at least one role.")
            return
        name = roles[index]
        confirm = messagebox.askyesno("Confirm", f"Remove role '{name}'?")
        if confirm:
            self.working_config['faculty_roles'].pop(index)
            self.show_faculty_roles()

    # ── CHANGE PIN ────────────────────────────────────────────────────────────

    def show_change_pin(self):
        self.clear_content()
        self.new_pin = ""
        self.entered_pin = ""

        tk.Label(self.content, text="Change PIN",
                font=("Arial", 18, "bold"), bg=BG_DARK, fg=WHITE).pack(pady=20)

        tk.Label(self.content, text="Enter your new PIN:",
                font=("Arial", 14), bg=BG_DARK, fg=SUBTLE).pack()

        self.pin_display = tk.Label(self.content, text="",
                font=("Arial", 28, "bold"), bg=BG_DARK, fg=WHITE)
        self.pin_display.pack(pady=10)

        self.add_numpad(self.content, self.change_pin_press)

        tk.Button(self.content, text="Back", font=("Arial", 12),
                 bg=BLUE, fg=WHITE, width=10,
                 command=self.show_main_menu).pack(pady=5)

    def change_pin_press(self, btn):
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
                messagebox.showinfo("Confirm PIN", "Please enter your new PIN again to confirm.")
            else:
                if self.entered_pin == self.new_pin:
                    self.working_config['pin'] = self.new_pin
                    messagebox.showinfo("PIN Updated", "PIN has been updated.\nRemember to click Save & Exit.")
                    self.show_main_menu()
                else:
                    messagebox.showerror("PIN Mismatch", "PINs did not match. Please try again.")
                    self.new_pin = ""
                    self.entered_pin = ""
                    self.pin_display.config(text="")
                    return
        else:
            self.entered_pin += btn
        try:
            self.pin_display.config(text='●' * len(self.entered_pin))
        except tk.TclError:
            pass

    # ── SAVE & EXIT ───────────────────────────────────────────────────────────

    def save_and_exit(self):
        confirm = messagebox.askyesno(
            "Save Changes",
            "Save all changes to config.json?\n\nThe badge listener will need to be restarted for changes to take effect."
        )
        if confirm:
            if save_config(self.working_config):
                messagebox.showinfo("Saved", "Configuration saved successfully!")
                self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.lift()
        root.attributes('-topmost', True)
        app = ReconfigureApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──