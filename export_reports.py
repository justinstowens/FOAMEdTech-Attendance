import os
import shutil
import string
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Colors
BG_DARK = "#1B2A4A"
BG_MID  = "#2471A3"
WHITE   = "#FFFFFF"

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

# Use install_path from config if available
if CONFIG and CONFIG.get('install_path'):
    BASE_DIR = CONFIG['install_path']

REPORTS_DIR = os.path.join(BASE_DIR, "Reports")
ARCHIVE_DIR = os.path.join(BASE_DIR, "Archive")

# Ensure Archive directory exists
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

def find_usb_drive():
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive) and drive != "C:\\":
            try:
                import ctypes
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                if drive_type == 2:
                    return drive
            except:
                continue
    return None

def get_report_files():
    if not os.path.exists(REPORTS_DIR):
        return []
    return [f for f in os.listdir(REPORTS_DIR) if f.endswith('.csv')]

def export_reports():
    report_files = get_report_files()
    if not report_files:
        messagebox.showwarning(
            "No Reports Found",
            "No reports found in the Reports folder.\nNothing to export."
        )
        return

    usb_drive = find_usb_drive()
    if not usb_drive:
        messagebox.showwarning(
            "No USB Drive Found",
            "No USB drive detected.\nPlease insert a USB drive and try again."
        )
        return

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    usb_folder = os.path.join(usb_drive, f"AttendanceReports_{timestamp}")
    os.makedirs(usb_folder, exist_ok=True)

    copied = 0
    archived = 0
    errors = []

    for filename in report_files:
        src = os.path.join(REPORTS_DIR, filename)
        try:
            shutil.copy2(src, os.path.join(usb_folder, filename))
            copied += 1
            shutil.move(src, os.path.join(ARCHIVE_DIR, filename))
            archived += 1
        except Exception as e:
            errors.append(filename)

    if errors:
        messagebox.showerror(
            "Export Completed With Errors",
            f"Exported {copied} of {len(report_files)} reports.\n\n"
            f"The following files had errors:\n" + "\n".join(errors)
        )
    else:
        program_name = CONFIG.get('program_name', 'Attendance System') if CONFIG else 'Attendance System'
        messagebox.showinfo(
            "Export Complete",
            f"{program_name}\n\n"
            f"{copied} report(s) copied to USB drive.\n"
            f"{archived} report(s) archived locally.\n\n"
            f"Reports folder has been cleared."
        )

# Run
root = tk.Tk()
root.withdraw()
export_reports()
root.destroy()
# ── END OF CODE — DO NOT COPY BELOW THIS LINE ──