import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import json
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ROSTER_FILE = os.path.join(BASE_DIR, "roster.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_log.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "Reports")

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
SIDEBAR  = "#162238"

# Ensure Reports directory exists
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

CONFIG = load_config()

# ── DATA FUNCTIONS ────────────────────────────────────────────────────────────

def load_roster():
    roster = []
    try:
        with open(ROSTER_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                roster.append({
                    'badge_id': row['badge_id'].strip(),
                    'name': row['name'].strip(),
                    'status': row['status'].strip(),
                    'grad_year': row['grad_year'].strip(),
                    'subprogram': row['subprogram'].strip()
                })
    except Exception as e:
        messagebox.showerror("Error", f"Could not load roster:\n{e}")
    return roster

def save_roster(roster):
    try:
        with open(ROSTER_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['badge_id', 'name', 'status', 'grad_year', 'subprogram'])
            writer.writeheader()
            writer.writerows(roster)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not save roster:\n{e}")
        return False

def load_attendance(start_dt=None, end_dt=None):
    records = []
    if not os.path.exists(ATTENDANCE_FILE):
        return records
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if start_dt and end_dt:
                    record_dt = datetime.strptime(row['date'].strip(), '%m/%d/%Y')
                    if start_dt <= record_dt <= end_dt:
                        records.append(row)
                else:
                    records.append(row)
            except:
                continue
    return records

def get_date_range_input(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Select Date Range")
    dialog.geometry("400x220")
    dialog.configure(bg=BG_DARK)
    dialog.resizable(False, False)
    dialog.grab_set()

    result = {'start': None, 'end': None, 'confirmed': False}

    tk.Label(dialog, text="Select Date Range",
            font=("Arial", 16, "bold"),
            bg=BG_DARK, fg=WHITE).pack(pady=15)

    form = tk.Frame(dialog, bg=BG_DARK)
    form.pack(padx=30, fill=tk.X)

    tk.Label(form, text="Start Date (MM/DD/YYYY):",
            font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=0, sticky="w", pady=5)
    start_var = tk.StringVar()
    tk.Entry(form, textvariable=start_var, font=("Arial", 12), width=15).grid(row=0, column=1, padx=10)

    tk.Label(form, text="End Date (MM/DD/YYYY):",
            font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=1, column=0, sticky="w", pady=5)
    end_var = tk.StringVar()
    tk.Entry(form, textvariable=end_var, font=("Arial", 12), width=15).grid(row=1, column=1, padx=10)

    def confirm():
        try:
            start = datetime.strptime(start_var.get().strip(), '%m/%d/%Y')
            end = datetime.strptime(end_var.get().strip(), '%m/%d/%Y')
            if end < start:
                messagebox.showwarning("Invalid", "End date must be after start date.")
                return
            result['start'] = start
            result['end'] = end
            result['start_str'] = start_var.get().strip().replace('/', '-')
            result['end_str'] = end_var.get().strip().replace('/', '-')
            result['confirmed'] = True
            dialog.destroy()
        except ValueError:
            messagebox.showwarning("Invalid", "Please use MM/DD/YYYY format.")

    btn_frame = tk.Frame(dialog, bg=BG_DARK)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Confirm", font=("Arial", 12, "bold"),
             bg=GREEN, fg=WHITE, width=10,
             command=confirm).pack(side=tk.LEFT, padx=10)

    tk.Button(btn_frame, text="Cancel", font=("Arial", 12, "bold"),
             bg=RED, fg=WHITE, width=10,
             command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    dialog.wait_window()
    return result

# ── MAIN APP ──────────────────────────────────────────────────────────────────

class ScheduleManagerApp:
    def __init__(self, root):
        self.root = root
        program_name = CONFIG.get('program_name', 'Attendance System')
        footer_text = CONFIG.get('branding', {}).get('footer_text', '')

        self.root.title(f"Schedule Manager — {program_name}")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_DARK)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))

        # ── Header ──
        header = tk.Frame(self.root, bg=BG_MID, pady=10)
        header.pack(fill=tk.X)

        tk.Label(header, text="Schedule Manager",
                font=("Arial", 22, "bold"),
                bg=BG_MID, fg=WHITE).pack(side=tk.LEFT, padx=20)

        tk.Label(header, text=program_name,
                font=("Arial", 14),
                bg=BG_MID, fg=BG_LIGHT).pack(side=tk.RIGHT, padx=20)

        # ── Main area ──
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Sidebar ──
        sidebar = tk.Frame(main_frame, bg=SIDEBAR, width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # ── Content area ──
        self.content = tk.Frame(main_frame, bg=BG_DARK)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Footer ──
        if footer_text:
            tk.Frame(self.root, bg=BG_MID, height=2).pack(fill=tk.X, side=tk.BOTTOM)
            tk.Label(self.root, text=footer_text,
                    font=("Arial", 8),
                    bg=BG_DARK, fg=WHITE).pack(side=tk.BOTTOM, pady=3)

        # Build sidebar
        self.build_sidebar(sidebar)

        # Show default screen
        self.show_welcome()

    def build_sidebar(self, sidebar):
        def section_label(text):
            tk.Label(sidebar, text=text,
                    font=("Arial", 10, "bold"),
                    bg=SIDEBAR, fg=SUBTLE).pack(fill=tk.X, padx=10, pady=(15,2))

        def menu_btn(text, command):
            tk.Button(sidebar, text=text,
                     font=("Arial", 12),
                     bg=SIDEBAR, fg=WHITE,
                     relief=tk.FLAT,
                     anchor="w",
                     padx=15,
                     activebackground=BG_MID,
                     activeforeground=WHITE,
                     command=command).pack(fill=tk.X, pady=1)

        section_label("── ROSTER ──")
        menu_btn("Add Learner", self.show_add_learner)
        menu_btn("Batch Add", self.show_batch_add)
        menu_btn("Mark Inactive", self.show_mark_inactive)
        menu_btn("View Roster", self.show_view_roster)

        section_label("── REPORTS ──")
        menu_btn("Detailed - Single", self.show_detailed_single)
        menu_btn("Detailed - All", self.show_detailed_all)
        menu_btn("Summary - Single", self.show_summary_single)
        menu_btn("Summary - All", self.show_summary_all)
        menu_btn("Summary - By Program", self.show_summary_subprogram)

        section_label("── BATCH LOGIN ──")
        menu_btn("Select From List", self.show_batch_login_list)
        menu_btn("Type With Autofill", self.show_batch_login_autofill)

        section_label("──────────────")
        tk.Button(sidebar, text="Exit",
                 font=("Arial", 12, "bold"),
                 bg=RED, fg=WHITE,
                 relief=tk.FLAT,
                 anchor="w",
                 padx=15,
                 command=self.root.destroy).pack(fill=tk.X, pady=(10,1))

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def content_header(self, title):
        tk.Label(self.content, text=title,
                font=("Arial", 20, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=20, padx=20, anchor="w")
        tk.Frame(self.content, bg=BG_MID, height=2).pack(fill=tk.X, padx=20)

    def show_welcome(self):
        self.clear_content()

        tk.Label(self.content,
                text="Welcome to the Schedule Manager",
                font=("Arial", 24, "bold"),
                bg=BG_DARK, fg=WHITE).pack(pady=40)

        tk.Label(self.content,
                text="Select an option from the menu on the left.",
                font=("Arial", 15),
                bg=BG_DARK, fg=SUBTLE).pack()

        tk.Label(self.content,
                text="\nROSTER — Add, manage, and view learners\n\n"
                     "REPORTS — Generate attendance reports by date range\n\n"
                     "BATCH LOGIN — Manually log attendance for a group",
                font=("Arial", 13),
                bg=BG_DARK, fg=WHITE,
                justify=tk.LEFT).pack(pady=20, padx=60)

    # ── ROSTER FUNCTIONS ──────────────────────────────────────────────────────

    def show_add_learner(self):
        self.clear_content()
        self.content_header("Add Single Learner")

        categories = CONFIG.get('resident_categories', ['EM', 'EM/FM', 'EM/IM', 'Faculty'])

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(padx=40, pady=20, fill=tk.X)

        fields = {}

        def add_field(label, hint=""):
            tk.Label(form, text=label, font=("Arial", 13), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(10,2))
            if hint:
                tk.Label(form, text=hint, font=("Arial", 10, "italic"), bg=BG_DARK, fg=SUBTLE).pack(anchor="w")
            var = tk.StringVar()
            tk.Entry(form, textvariable=var, font=("Arial", 13), width=35).pack(anchor="w")
            return var

        fields['badge_id'] = add_field("Badge ID:")
        fields['name'] = add_field("Name:", "Format: LastName FirstName")
        fields['grad_year'] = add_field("Graduation Year:", "e.g. 2027 (use 2100 for Faculty)")

        tk.Label(form, text="Sub-program:", font=("Arial", 13), bg=BG_DARK, fg=SUBTLE).pack(anchor="w", pady=(10,2))
        subprogram_var = tk.StringVar(value=categories[0])
        tk.OptionMenu(form, subprogram_var, *categories).pack(anchor="w")

        def save():
            badge_id = fields['badge_id'].get().strip()
            name = fields['name'].get().strip()
            grad_year = fields['grad_year'].get().strip()
            subprogram = subprogram_var.get().strip()

            if not all([badge_id, name, grad_year, subprogram]):
                messagebox.showwarning("Missing Info", "Please fill in all fields.")
                return

            roster = load_roster()
            if any(r['badge_id'] == badge_id for r in roster):
                messagebox.showwarning("Duplicate", f"Badge ID {badge_id} already exists.")
                return

            roster.append({
                'badge_id': badge_id,
                'name': name,
                'status': 'active',
                'grad_year': grad_year,
                'subprogram': subprogram
            })

            if save_roster(roster):
                messagebox.showinfo("Success", f"{name} added successfully!")
                self.show_add_learner()

        tk.Button(form, text="Add Learner",
                 font=("Arial", 14, "bold"),
                 bg=GREEN, fg=WHITE, width=15,
                 command=save).pack(pady=20)

    def show_batch_add(self):
        self.clear_content()
        self.content_header("Batch Add Learners")

        categories = CONFIG.get('resident_categories', ['EM', 'EM/FM', 'EM/IM', 'Faculty'])

        tk.Label(self.content,
                text="Enter each learner's details and click Add. Click Done when finished.",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(padx=20, anchor="w")

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(padx=40, pady=10, fill=tk.X)

        # Input fields
        input_frame = tk.Frame(form, bg=BG_DARK)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Badge ID", font=("Arial", 11), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=0, padx=5, sticky="w")
        tk.Label(input_frame, text="Name (Last First)", font=("Arial", 11), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=1, padx=5, sticky="w")
        tk.Label(input_frame, text="Grad Year", font=("Arial", 11), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=2, padx=5, sticky="w")
        tk.Label(input_frame, text="Sub-program", font=("Arial", 11), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=3, padx=5, sticky="w")

        badge_var = tk.StringVar()
        name_var = tk.StringVar()
        year_var = tk.StringVar()
        subprogram_var = tk.StringVar(value=categories[0])

        tk.Entry(input_frame, textvariable=badge_var, font=("Arial", 12), width=12).grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=name_var, font=("Arial", 12), width=25).grid(row=1, column=1, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=year_var, font=("Arial", 12), width=8).grid(row=1, column=2, padx=5, pady=5)
        tk.OptionMenu(input_frame, subprogram_var, *categories).grid(row=1, column=3, padx=5, pady=5)

        # Added list
        added_label = tk.Label(form, text="Added so far: 0",
                              font=("Arial", 12, "bold"), bg=BG_DARK, fg=WHITE)
        added_label.pack(anchor="w", pady=5)

        list_frame = tk.Frame(form, bg=BG_DARK)
        list_frame.pack(fill=tk.X)

        added = []

        def add_one():
            badge_id = badge_var.get().strip()
            name = name_var.get().strip()
            grad_year = year_var.get().strip()
            subprogram = subprogram_var.get().strip()

            if not all([badge_id, name, grad_year]):
                messagebox.showwarning("Missing Info", "Please fill in all fields.")
                return

            roster = load_roster()
            if any(r['badge_id'] == badge_id for r in roster):
                messagebox.showwarning("Duplicate", f"Badge ID {badge_id} already exists — skipping.")
                return

            if any(a['badge_id'] == badge_id for a in added):
                messagebox.showwarning("Duplicate", f"Badge ID {badge_id} already in this batch.")
                return

            added.append({
                'badge_id': badge_id,
                'name': name,
                'status': 'active',
                'grad_year': grad_year,
                'subprogram': subprogram
            })

            tk.Label(list_frame, text=f"✓ {name} ({badge_id}) — {subprogram}",
                    font=("Arial", 11), bg=BG_DARK, fg=GREEN).pack(anchor="w")

            added_label.config(text=f"Added so far: {len(added)}")
            badge_var.set("")
            name_var.set("")
            year_var.set("")

        def save_all():
            if not added:
                messagebox.showwarning("Nothing to save", "No learners have been added yet.")
                return
            roster = load_roster()
            roster.extend(added)
            if save_roster(roster):
                messagebox.showinfo("Success", f"{len(added)} learner(s) added successfully!")
                self.show_batch_add()

        btn_frame = tk.Frame(form, bg=BG_DARK)
        btn_frame.pack(pady=15, fill=tk.X)

        tk.Button(btn_frame, text="+ Add to Batch",
                 font=("Arial", 13, "bold"),
                 bg=BLUE, fg=WHITE, width=15,
                 command=add_one).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Save All",
                 font=("Arial", 13, "bold"),
                 bg=GREEN, fg=WHITE, width=15,
                 command=save_all).pack(side=tk.LEFT, padx=5)

    def show_mark_inactive(self):
        self.clear_content()
        self.content_header("Mark Learners Inactive")

        roster = load_roster()
        active = [r for r in roster if r['status'] == 'active']

        tk.Label(self.content,
                text="Select learners to mark as inactive. Their attendance history will be preserved.",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(padx=20, anchor="w")

        container = tk.Frame(self.content, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        check_vars = []
        for r in sorted(active, key=lambda x: x['name']):
            var = tk.BooleanVar()
            check_vars.append((var, r['badge_id'], r['name']))
            tk.Checkbutton(scroll_frame,
                          text=f"{r['name']}   ({r['subprogram']})   Grad: {r['grad_year']}",
                          variable=var,
                          font=("Arial", 12),
                          bg=BG_DARK, fg=WHITE,
                          selectcolor=BG_MID,
                          activebackground=BG_DARK,
                          activeforeground=WHITE).pack(anchor="w", pady=3)

        def mark_selected():
            selected = [(badge_id, name) for var, badge_id, name in check_vars if var.get()]
            if not selected:
                messagebox.showwarning("Nothing selected", "Please select at least one learner.")
                return

            names = "\n".join(f"  • {name}" for _, name in selected)
            confirm = messagebox.askyesno("Confirm",
                f"Mark the following learners as inactive?\n\n{names}")
            if not confirm:
                return

            for r in roster:
                if any(r['badge_id'] == bid for bid, _ in selected):
                    r['status'] = 'inactive'

            if save_roster(roster):
                messagebox.showinfo("Success", f"{len(selected)} learner(s) marked inactive.")
                self.show_mark_inactive()

        tk.Button(self.content, text="Mark Selected Inactive",
                 font=("Arial", 14, "bold"),
                 bg=RED, fg=WHITE, width=20,
                 command=mark_selected).pack(pady=10)

    def show_view_roster(self):
        self.clear_content()
        self.content_header("View Roster")

        roster = load_roster()
        active = [r for r in roster if r['status'] == 'active']
        inactive = [r for r in roster if r['status'] == 'inactive']

        # Filter controls
        filter_frame = tk.Frame(self.content, bg=BG_DARK)
        filter_frame.pack(padx=20, pady=5, fill=tk.X)

        show_var = tk.StringVar(value="Active")
        tk.Label(filter_frame, text="Show:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(side=tk.LEFT)
        for option in ["Active", "Inactive", "All"]:
            tk.Radiobutton(filter_frame, text=option, variable=show_var, value=option,
                          font=("Arial", 12), bg=BG_DARK, fg=WHITE,
                          selectcolor=BG_MID, activebackground=BG_DARK,
                          command=lambda: refresh_list()).pack(side=tk.LEFT, padx=10)

        # Table
        container = tk.Frame(self.content, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background=BG_DARK,
                        foreground=WHITE,
                        fieldbackground=BG_DARK,
                        font=("Arial", 11))
        style.configure("Treeview.Heading",
                        background=BG_MID,
                        foreground=WHITE,
                        font=("Arial", 11, "bold"))

        tree = ttk.Treeview(container,
                           columns=("badge_id", "name", "subprogram", "grad_year", "status"),
                           show="headings")

        for col, heading, width in [
            ("badge_id", "Badge ID", 120),
            ("name", "Name", 200),
            ("subprogram", "Sub-program", 120),
            ("grad_year", "Grad Year", 100),
            ("status", "Status", 100)
        ]:
            tree.heading(col, text=heading)
            tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh_list():
            for row in tree.get_children():
                tree.delete(row)
            show = show_var.get()
            if show == "Active":
                data = sorted(active, key=lambda x: x['name'])
            elif show == "Inactive":
                data = sorted(inactive, key=lambda x: x['name'])
            else:
                data = sorted(roster, key=lambda x: x['name'])
            for r in data:
                tree.insert("", tk.END, values=(
                    r['badge_id'], r['name'], r['subprogram'],
                    r['grad_year'], r['status']
                ))

        tk.Label(self.content,
                text=f"Active: {len(active)}   |   Inactive: {len(inactive)}   |   Total: {len(roster)}",
                font=("Arial", 12, "bold"), bg=BG_DARK, fg=SUBTLE).pack(pady=5)

        refresh_list()

    # ── REPORT FUNCTIONS ──────────────────────────────────────────────────────

    def display_report(self, title, headers, rows, filename):
        self.clear_content()
        self.content_header(title)

        if not rows:
            tk.Label(self.content, text="No records found for the selected date range.",
                    font=("Arial", 14), bg=BG_DARK, fg=SUBTLE).pack(pady=20)
            return

        container = tk.Frame(self.content, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background=BG_DARK,
                        foreground=WHITE,
                        fieldbackground=BG_DARK,
                        font=("Arial", 11))
        style.configure("Treeview.Heading",
                        background=BG_MID,
                        foreground=WHITE,
                        font=("Arial", 11, "bold"))

        tree = ttk.Treeview(container, columns=headers, show="headings")
        for h in headers:
            tree.heading(h, text=h.replace('_', ' ').title())
            tree.column(h, width=120)

        scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        for row in rows:
            tree.insert("", tk.END, values=row)

        # Save to CSV
        filepath = os.path.join(REPORTS_DIR, filename)
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            tk.Label(self.content,
                    text=f"✓ Report saved to Reports folder: {filename}",
                    font=("Arial", 11), bg=BG_DARK, fg=GREEN).pack(pady=5)
        except Exception as e:
            tk.Label(self.content,
                    text=f"⚠ Could not save report: {e}",
                    font=("Arial", 11), bg=BG_DARK, fg=RED).pack(pady=5)

        tk.Label(self.content,
                text=f"Total records: {len(rows)}",
                font=("Arial", 12, "bold"), bg=BG_DARK, fg=SUBTLE).pack(pady=5)

    def show_detailed_single(self):
        search = tk.simpledialog.askstring("Learner Search",
            "Enter learner name or badge ID:",
            parent=self.root)
        if not search:
            return

        dr = get_date_range_input(self.root)
        if not dr['confirmed']:
            return

        records = load_attendance(dr['start'], dr['end'])
        filtered = [r for r in records
                   if search.lower() in r['name'].lower()
                   or search == r['badge_id'].strip()]

        if not filtered:
            messagebox.showinfo("No Results", "No records found for that learner in this date range.")
            return

        learner_name = filtered[0]['name'].replace(' ', '_')
        filename = f"detailed_{learner_name}_{dr['start_str']}_to_{dr['end_str']}.csv"
        headers = ['date', 'time_in', 'badge_id', 'name', 'subprogram', 'hours_credited']
        rows = [(r['date'], r['time_in'], r['badge_id'], r['name'],
                r['subprogram'], r['hours_credited']) for r in filtered]

        self.display_report(f"Detailed Report — {filtered[0]['name']}", headers, rows, filename)

    def show_detailed_all(self):
        dr = get_date_range_input(self.root)
        if not dr['confirmed']:
            return

        records = load_attendance(dr['start'], dr['end'])
        if not records:
            messagebox.showinfo("No Results", "No records found in this date range.")
            return

        filename = f"detailed_all_learners_{dr['start_str']}_to_{dr['end_str']}.csv"
        headers = ['date', 'time_in', 'badge_id', 'name', 'subprogram', 'hours_credited']
        rows = sorted([(r['date'], r['time_in'], r['badge_id'], r['name'],
                r['subprogram'], r['hours_credited']) for r in records],
               key=lambda x: (x[3], x[0]))

        self.display_report("Detailed Report — All Learners", headers, rows, filename)

    def show_summary_single(self):
        search = tk.simpledialog.askstring("Learner Search",
            "Enter learner name or badge ID:",
            parent=self.root)
        if not search:
            return

        dr = get_date_range_input(self.root)
        if not dr['confirmed']:
            return

        records = load_attendance(dr['start'], dr['end'])
        filtered = [r for r in records
                   if search.lower() in r['name'].lower()
                   or search == r['badge_id'].strip()]

        if not filtered:
            messagebox.showinfo("No Results", "No records found for that learner in this date range.")
            return

        total_hours = 0.0
        for r in filtered:
            try:
                total_hours += float(r['hours_credited'])
            except:
                pass

        learner = filtered[0]
        learner_name = learner['name'].replace(' ', '_')
        filename = f"summary_{learner_name}_{dr['start_str']}_to_{dr['end_str']}.csv"
        headers = ['name', 'subprogram', 'grad_year', 'date_range', 'sessions', 'total_hours']
        rows = [(learner['name'], learner['subprogram'], learner['grad_year'],
                f"{dr['start_str']} to {dr['end_str']}", len(filtered), f"{total_hours:.1f}")]

        self.display_report(f"Summary — {learner['name']}", headers, rows, filename)

    def show_summary_all(self):
        dr = get_date_range_input(self.root)
        if not dr['confirmed']:
            return

        records = load_attendance(dr['start'], dr['end'])
        if not records:
            messagebox.showinfo("No Results", "No records found in this date range.")
            return

        summary = {}
        for r in records:
            bid = r['badge_id'].strip()
            if bid not in summary:
                summary[bid] = {
                    'name': r['name'],
                    'subprogram': r['subprogram'],
                    'grad_year': r['grad_year'],
                    'sessions': 0,
                    'total_hours': 0.0
                }
            summary[bid]['sessions'] += 1
            try:
                summary[bid]['total_hours'] += float(r['hours_credited'])
            except:
                pass

        filename = f"summary_all_learners_{dr['start_str']}_to_{dr['end_str']}.csv"
        headers = ['name', 'subprogram', 'grad_year', 'sessions', 'total_hours']
        rows = sorted([(s['name'], s['subprogram'], s['grad_year'],
                s['sessions'], f"{s['total_hours']:.1f}")
               for s in summary.values()],
               key=lambda x: x[0])

        self.display_report("Summary — All Learners", headers, rows, filename)

    def show_summary_subprogram(self):
        dr = get_date_range_input(self.root)
        if not dr['confirmed']:
            return

        records = load_attendance(dr['start'], dr['end'])
        if not records:
            messagebox.showinfo("No Results", "No records found in this date range.")
            return

        summary = {}
        for r in records:
            bid = r['badge_id'].strip()
            if bid not in summary:
                summary[bid] = {
                    'name': r['name'],
                    'subprogram': r['subprogram'],
                    'grad_year': r['grad_year'],
                    'sessions': 0,
                    'total_hours': 0.0
                }
            summary[bid]['sessions'] += 1
            try:
                summary[bid]['total_hours'] += float(r['hours_credited'])
            except:
                pass

        filename = f"summary_by_subprogram_{dr['start_str']}_to_{dr['end_str']}.csv"
        headers = ['subprogram', 'name', 'grad_year', 'sessions', 'total_hours']
        rows = sorted([(s['subprogram'], s['name'], s['grad_year'],
                s['sessions'], f"{s['total_hours']:.1f}")
               for s in summary.values()],
               key=lambda x: (x[0], x[1]))

        self.display_report("Summary — By Sub-program", headers, rows, filename)

    # ── BATCH LOGIN ───────────────────────────────────────────────────────────

    def show_batch_login_list(self):
        self.clear_content()
        self.content_header("Batch Login — Select From List")

        session_types = CONFIG.get('session_types', [{'name': 'Conference'}, {'name': 'Journal Club'}])
        session_names = [s['name'] for s in session_types]

        top_frame = tk.Frame(self.content, bg=BG_DARK)
        top_frame.pack(padx=20, pady=10, fill=tk.X)

        # Session type
        tk.Label(top_frame, text="Session Type:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        session_var = tk.StringVar(value=session_names[0])
        tk.OptionMenu(top_frame, session_var, *session_names).grid(row=0, column=1, sticky="w", padx=5)

        # Date
        tk.Label(top_frame, text="Date (MM/DD/YYYY):", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime('%m/%d/%Y'))
        tk.Entry(top_frame, textvariable=date_var, font=("Arial", 12), width=15).grid(row=1, column=1, sticky="w", padx=5)

        # Time
        tk.Label(top_frame, text="Time (HH:MM AM/PM):", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        time_var = tk.StringVar(value="08:00 AM")
        tk.Entry(top_frame, textvariable=time_var, font=("Arial", 12), width=15).grid(row=2, column=1, sticky="w", padx=5)

        # Roster list with checkboxes
        tk.Label(self.content, text="Select learners:",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(padx=20, anchor="w")

        roster = load_roster()
        active = sorted([r for r in roster if r['status'] == 'active'], key=lambda x: x['name'])

        container = tk.Frame(self.content, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        check_vars = []
        for r in active:
            var = tk.BooleanVar()
            check_vars.append((var, r))
            tk.Checkbutton(scroll_frame,
                          text=f"{r['name']}   ({r['subprogram']})",
                          variable=var,
                          font=("Arial", 12),
                          bg=BG_DARK, fg=WHITE,
                          selectcolor=BG_MID,
                          activebackground=BG_DARK,
                          activeforeground=WHITE).pack(anchor="w", pady=2)

        def submit():
            selected = [(var.get(), r) for var, r in check_vars if var.get()]
            if not selected:
                messagebox.showwarning("Nothing selected", "Please select at least one learner.")
                return

            try:
                date_str = date_var.get().strip()
                time_str = time_var.get().strip().upper()
                datetime.strptime(date_str, '%m/%d/%Y')
                time_obj = datetime.strptime(time_str, '%I:%M %p')
            except ValueError:
                messagebox.showwarning("Invalid", "Please check date and time format.")
                return

            session_name = session_var.get()
            session_cfg = next((s for s in session_types if s['name'] == session_name), session_types[0])
            tracks_hours = session_cfg.get('tracks_hours', True)
            log_label = session_cfg.get('log_label', session_name)

            if tracks_hours:
                start_hour = session_cfg.get('start_hour', 8)
                total_hours = session_cfg.get('total_hours', 5)
                hours_credited = str(max(0, min(total_hours, total_hours - (time_obj.hour - start_hour))))
            else:
                hours_credited = log_label

            logged = 0
            skipped = 0

            for _, r in [(v, r) for v, r in check_vars if v.get()]:
                # Check duplicate
                duplicate = False
                if os.path.exists(ATTENDANCE_FILE):
                    with open(ATTENDANCE_FILE, newline='') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['badge_id'].strip() == r['badge_id'] and row['date'].strip() == date_str:
                                duplicate = True
                                break

                if duplicate:
                    answer = messagebox.askyesno("Duplicate",
                        f"{r['name']} already has an entry for {date_str}.\nAdd anyway?")
                    if not answer:
                        skipped += 1
                        continue

                try:
                    file_exists = os.path.exists(ATTENDANCE_FILE)
                    with open(ATTENDANCE_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(['date', 'time_in', 'badge_id', 'name',
                                           'status', 'grad_year', 'subprogram', 'hours_credited', 'roles'])
                        writer.writerow([date_str, time_str, r['badge_id'], r['name'],
                                       r['status'], r['grad_year'], r['subprogram'], hours_credited, ''])
                    logged += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Could not log {r['name']}: {e}")

            messagebox.showinfo("Complete", f"Logged: {logged}\nSkipped: {skipped}")
            self.show_batch_login_list()

        tk.Button(self.content, text="Submit Batch",
                 font=("Arial", 14, "bold"),
                 bg=GREEN, fg=WHITE, width=15,
                 command=submit).pack(pady=10)

    def show_batch_login_autofill(self):
        self.clear_content()
        self.content_header("Batch Login — Type With Autofill")

        session_types = CONFIG.get('session_types', [{'name': 'Conference'}, {'name': 'Journal Club'}])
        session_names = [s['name'] for s in session_types]

        top_frame = tk.Frame(self.content, bg=BG_DARK)
        top_frame.pack(padx=20, pady=10, fill=tk.X)

        tk.Label(top_frame, text="Session Type:", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        session_var = tk.StringVar(value=session_names[0])
        tk.OptionMenu(top_frame, session_var, *session_names).grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(top_frame, text="Date (MM/DD/YYYY):", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime('%m/%d/%Y'))
        tk.Entry(top_frame, textvariable=date_var, font=("Arial", 12), width=15).grid(row=1, column=1, sticky="w", padx=5)

        tk.Label(top_frame, text="Time (HH:MM AM/PM):", font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        time_var = tk.StringVar(value="08:00 AM")
        tk.Entry(top_frame, textvariable=time_var, font=("Arial", 12), width=15).grid(row=2, column=1, sticky="w", padx=5)

        roster = load_roster()
        active = [r for r in roster if r['status'] == 'active']

        search_frame = tk.Frame(self.content, bg=BG_DARK)
        search_frame.pack(padx=20, pady=10, fill=tk.X)

        tk.Label(search_frame, text="Type name to search:",
                font=("Arial", 12), bg=BG_DARK, fg=SUBTLE).pack(anchor="w")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var,
                               font=("Arial", 13), width=30)
        search_entry.pack(side=tk.LEFT, pady=5)

        match_frame = tk.Frame(self.content, bg=BG_DARK)
        match_frame.pack(padx=20, fill=tk.X)

        added = []
        added_frame = tk.Frame(self.content, bg=BG_DARK)
        added_frame.pack(padx=20, fill=tk.X)

        added_label = tk.Label(added_frame, text="Added: 0",
                              font=("Arial", 12, "bold"), bg=BG_DARK, fg=WHITE)
        added_label.pack(anchor="w", pady=5)

        def update_matches(*args):
            for w in match_frame.winfo_children():
                w.destroy()
            search = search_var.get().strip().lower()
            if not search:
                return
            matches = [r for r in active if search in r['name'].lower()][:5]
            for r in matches:
                tk.Button(match_frame,
                         text=f"{r['name']} ({r['subprogram']})",
                         font=("Arial", 12),
                         bg=BLUE, fg=WHITE,
                         command=lambda r=r: add_learner(r)).pack(anchor="w", pady=2)

        def add_learner(r):
            if any(a['badge_id'] == r['badge_id'] for a in added):
                messagebox.showwarning("Duplicate", f"{r['name']} already in batch.")
                return
            added.append(r)
            tk.Label(added_frame,
                    text=f"✓ {r['name']} ({r['subprogram']})",
                    font=("Arial", 11), bg=BG_DARK, fg=GREEN).pack(anchor="w")
            added_label.config(text=f"Added: {len(added)}")
            search_var.set("")
            for w in match_frame.winfo_children():
                w.destroy()

        search_var.trace('w', update_matches)

        def submit():
            if not added:
                messagebox.showwarning("Nothing to save", "No learners added yet.")
                return

            try:
                date_str = date_var.get().strip()
                time_str = time_var.get().strip().upper()
                datetime.strptime(date_str, '%m/%d/%Y')
                time_obj = datetime.strptime(time_str, '%I:%M %p')
            except ValueError:
                messagebox.showwarning("Invalid", "Please check date and time format.")
                return

            session_name = session_var.get()
            session_cfg = next((s for s in session_types if s['name'] == session_name), session_types[0])
            tracks_hours = session_cfg.get('tracks_hours', True)
            log_label = session_cfg.get('log_label', session_name)

            if tracks_hours:
                start_hour = session_cfg.get('start_hour', 8)
                total_hours = session_cfg.get('total_hours', 5)
                hours_credited = str(max(0, min(total_hours, total_hours - (time_obj.hour - start_hour))))
            else:
                hours_credited = log_label

            logged = 0
            skipped = 0

            for r in added:
                duplicate = False
                if os.path.exists(ATTENDANCE_FILE):
                    with open(ATTENDANCE_FILE, newline='') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['badge_id'].strip() == r['badge_id'] and row['date'].strip() == date_str:
                                duplicate = True
                                break

                if duplicate:
                    answer = messagebox.askyesno("Duplicate",
                        f"{r['name']} already has an entry for {date_str}.\nAdd anyway?")
                    if not answer:
                        skipped += 1
                        continue

                try:
                    file_exists = os.path.exists(ATTENDANCE_FILE)
                    with open(ATTENDANCE_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(['date', 'time_in', 'badge_id', 'name',
                                           'status', 'grad_year', 'subprogram', 'hours_credited', 'roles'])
                        writer.writerow([date_str, time_str, r['badge_id'], r['name'],
                                       r['status'], r['grad_year'], r['subprogram'], hours_credited, ''])
                    logged += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Could not log {r['name']}: {e}")

            messagebox.showinfo("Complete", f"Logged: {logged}\nSkipped: {skipped}")
            self.show_batch_login_autofill()

        tk.Button(self.content, text="Submit Batch",
                 font=("Arial", 14, "bold"),
                 bg=GREEN, fg=WHITE, width=15,
                 command=submit).pack(pady=10)

if __name__ == "__main__":
    try:
        import tkinter.simpledialog
        root = tk.Tk()
        root.lift()
        app = ScheduleManagerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──