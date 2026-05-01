import csv
import os
import json
from datetime import datetime

# File paths and config
BASE_DIR = r"C:\AttendanceSystem"
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ROSTER_FILE = os.path.join(BASE_DIR, "roster.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_log.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "Reports")

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ERROR loading config: {e}")
        return None

CONFIG = load_config()

# Ensure Reports directory exists
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# ── ROSTER FUNCTIONS ──────────────────────────────────────────────────────────

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
        print(f"  ERROR loading roster: {e}")
    return roster

def save_roster(roster):
    try:
        with open(ROSTER_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['badge_id', 'name', 'status', 'grad_year', 'subprogram'])
            writer.writeheader()
            writer.writerows(roster)
        return True
    except Exception as e:
        print(f"  ERROR saving roster: {e}")
        return False

def view_roster():
    roster = load_roster()
    active = [r for r in roster if r['status'] == 'active']
    inactive = [r for r in roster if r['status'] == 'inactive']

    print()
    print("=" * 70)
    print(f"  ACTIVE LEARNERS ({len(active)})")
    print("=" * 70)
    print(f"  {'Badge ID':<12} {'Name':<30} {'Grad Year':<12} {'Subprogram'}")
    print("-" * 70)
    for r in sorted(active, key=lambda x: x['name']):
        print(f"  {r['badge_id']:<12} {r['name']:<30} {r['grad_year']:<12} {r['subprogram']}")

    print()
    print("=" * 70)
    print(f"  INACTIVE LEARNERS ({len(inactive)})")
    print("=" * 70)
    print(f"  {'Badge ID':<12} {'Name':<30} {'Grad Year':<12} {'Subprogram'}")
    print("-" * 70)
    for r in sorted(inactive, key=lambda x: x['name']):
        print(f"  {r['badge_id']:<12} {r['name']:<30} {r['grad_year']:<12} {r['subprogram']}")
    print()

def add_single_learner():
    print()
    print("  ADD SINGLE LEARNER")
    print("-" * 40)
    badge_id = input("  Badge ID: ").strip()
    name = input("  Name (LastName FirstName): ").strip()
    grad_year = input("  Graduation Year: ").strip()
    print("  Sub-programs: EM, EM/FM, EM/IM, Faculty")
    subprogram = input("  Sub-program: ").strip()

    roster = load_roster()

    # Check for duplicate
    if any(r['badge_id'] == badge_id for r in roster):
        print(f"  ⚠ Badge ID {badge_id} already exists in roster!")
        return

    roster.append({
        'badge_id': badge_id,
        'name': name,
        'status': 'active',
        'grad_year': grad_year,
        'subprogram': subprogram
    })

    if save_roster(roster):
        print(f"  ✓ {name} added successfully!")
    print()

def batch_add_learners():
    print()
    print("  BATCH ADD LEARNERS")
    print("  Type 'done' for Badge ID when finished")
    print("-" * 40)

    roster = load_roster()
    added = 0

    while True:
        badge_id = input("  Badge ID (or 'done'): ").strip()
        if badge_id.lower() == 'done':
            break

        # Check for duplicate
        if any(r['badge_id'] == badge_id for r in roster):
            print(f"  ⚠ Badge ID {badge_id} already exists — skipping")
            continue

        name = input("  Name (LastName FirstName): ").strip()
        grad_year = input("  Graduation Year: ").strip()
        print("  Sub-programs: EM, EM/FM, EM/IM, Faculty")
        subprogram = input("  Sub-program: ").strip()

        roster.append({
            'badge_id': badge_id,
            'name': name,
            'status': 'active',
            'grad_year': grad_year,
            'subprogram': subprogram
        })
        added += 1
        print(f"  ✓ {name} added — continue or type 'done'")
        print()

    if added > 0 and save_roster(roster):
        print(f"  ✓ {added} learner(s) added successfully!")
    print()

def mark_inactive_single():
    print()
    print("  MARK SINGLE LEARNER INACTIVE")
    print("-" * 40)
    search = input("  Enter name or badge ID: ").strip().lower()

    roster = load_roster()
    matches = [r for r in roster if search in r['name'].lower() or search == r['badge_id']]

    if not matches:
        print("  ⚠ No matching learner found!")
        return

    if len(matches) > 1:
        print("  Multiple matches found:")
        for i, r in enumerate(matches):
            print(f"  {i+1}. {r['name']} ({r['badge_id']})")
        choice = int(input("  Select number: ")) - 1
        target = matches[choice]
    else:
        target = matches[0]

    confirm = input(f"  Mark {target['name']} as inactive? (yes/no): ").strip().lower()
    if confirm == 'yes':
        for r in roster:
            if r['badge_id'] == target['badge_id']:
                r['status'] = 'inactive'
        if save_roster(roster):
            print(f"  ✓ {target['name']} marked as inactive!")
    else:
        print("  Cancelled.")
    print()

def batch_mark_inactive():
    print()
    print("  BATCH MARK LEARNERS INACTIVE")
    print("  Type 'done' when finished")
    print("-" * 40)

    roster = load_roster()
    updated = 0

    while True:
        search = input("  Enter name or badge ID (or 'done'): ").strip().lower()
        if search == 'done':
            break

        matches = [r for r in roster if search in r['name'].lower() or search == r['badge_id']]

        if not matches:
            print("  ⚠ No matching learner found — try again")
            continue

        if len(matches) > 1:
            print("  Multiple matches found:")
            for i, r in enumerate(matches):
                print(f"  {i+1}. {r['name']} ({r['badge_id']})")
            choice = int(input("  Select number: ")) - 1
            target = matches[choice]
        else:
            target = matches[0]

        for r in roster:
            if r['badge_id'] == target['badge_id']:
                r['status'] = 'inactive'
        updated += 1
        print(f"  ✓ {target['name']} marked inactive — continue or type 'done'")

    if updated > 0 and save_roster(roster):
        print(f"  ✓ {updated} learner(s) marked inactive!")
    print()

# ── REPORT FUNCTIONS ──────────────────────────────────────────────────────────

def get_date_range():
    print()
    while True:
        try:
            start = input("  Start date (MM/DD/YYYY): ").strip()
            end = input("  End date (MM/DD/YYYY): ").strip()
            start_dt = datetime.strptime(start, '%m/%d/%Y')
            end_dt = datetime.strptime(end, '%m/%d/%Y')
            if end_dt < start_dt:
                print("  ⚠ End date must be after start date — try again")
                continue
            return start_dt, end_dt, start.replace('/', '-'), end.replace('/', '-')
        except ValueError:
            print("  ⚠ Invalid date format — please use MM/DD/YYYY")

def load_attendance(start_dt, end_dt):
    records = []
    if not os.path.exists(ATTENDANCE_FILE):
        print("  ⚠ No attendance log found!")
        return records
    with open(ATTENDANCE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record_dt = datetime.strptime(row['date'].strip(), '%m/%d/%Y')
                if start_dt <= record_dt <= end_dt:
                    records.append(row)
            except:
                continue
    return records

def detailed_report_single():
    print()
    print("  DETAILED REPORT — SINGLE LEARNER")
    print("-" * 40)
    search = input("  Enter name or badge ID: ").strip().lower()
    start_dt, end_dt, start_str, end_str = get_date_range()

    records = load_attendance(start_dt, end_dt)
    filtered = [r for r in records if search in r['name'].lower() or search == r['badge_id'].strip()]

    if not filtered:
        print("  ⚠ No records found for that learner in this date range!")
        return

    learner_name = filtered[0]['name'].replace(' ', '_')
    filename = f"detailed_{learner_name}_{start_str}_to_{end_str}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    # Print to screen
    print()
    print("=" * 70)
    print(f"  {'Date':<14} {'Time':<12} {'Name':<25} {'Subprogram':<12} {'Hrs'}")
    print("-" * 70)
    for r in filtered:
        print(f"  {r['date']:<14} {r['time_in']:<12} {r['name']:<25} {r['subprogram']:<12} {r['hours_credited']}")
    print("=" * 70)
    print(f"  Total records: {len(filtered)}")
    print()

    # Save to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'time_in', 'badge_id', 'name', 'status', 'grad_year', 'subprogram', 'hours_credited', 'roles'])
        writer.writeheader()
        writer.writerows(filtered)

    print(f"  ✓ Report saved to: {filepath}")
    print()

def detailed_report_all():
    print()
    print("  DETAILED REPORT — ALL LEARNERS")
    print("-" * 40)
    start_dt, end_dt, start_str, end_str = get_date_range()

    records = load_attendance(start_dt, end_dt)

    if not records:
        print("  ⚠ No records found in this date range!")
        return

    filename = f"detailed_all_learners_{start_str}_to_{end_str}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    # Print to screen
    print()
    print("=" * 70)
    print(f"  {'Date':<14} {'Time':<12} {'Name':<25} {'Subprogram':<12} {'Hrs'}")
    print("-" * 70)
    for r in sorted(records, key=lambda x: (x['name'], x['date'])):
        print(f"  {r['date']:<14} {r['time_in']:<12} {r['name']:<25} {r['subprogram']:<12} {r['hours_credited']}")
    print("=" * 70)
    print(f"  Total records: {len(records)}")
    print()

    # Save to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'time_in', 'badge_id', 'name', 'status', 'grad_year', 'subprogram', 'hours_credited', 'roles'])
        writer.writeheader()
        writer.writerows(sorted(records, key=lambda x: (x['name'], x['date'])))

    print(f"  ✓ Report saved to: {filepath}")
    print()

def summary_report_single():
    print()
    print("  HOURS SUMMARY — SINGLE LEARNER")
    print("-" * 40)
    search = input("  Enter name or badge ID: ").strip().lower()
    start_dt, end_dt, start_str, end_str = get_date_range()

    records = load_attendance(start_dt, end_dt)
    filtered = [r for r in records if search in r['name'].lower() or search == r['badge_id'].strip()]

    if not filtered:
        print("  ⚠ No records found for that learner in this date range!")
        return

    total_hours = sum(float(r['hours_credited']) for r in filtered if r['hours_credited'] not in ['Journal Club', ''] and r['hours_credited'].replace('.','',1).isdigit())
    learner = filtered[0]
    learner_name = learner['name'].replace(' ', '_')

    filename = f"summary_{learner_name}_{start_str}_to_{end_str}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    # Print to screen
    print()
    print("=" * 70)
    print(f"  Name:       {learner['name']}")
    print(f"  Sub-program: {learner['subprogram']}")
    print(f"  Grad Year:  {learner['grad_year']}")
    print(f"  Date Range: {start_str} to {end_str}")
    print(f"  Sessions:   {len(filtered)}")
    print(f"  Total Hours: {total_hours:.1f}")
    print("=" * 70)
    print()

    # Save to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'subprogram', 'grad_year', 'date_range', 'sessions', 'total_hours'])
        writer.writerow([
            learner['name'],
            learner['subprogram'],
            learner['grad_year'],
            f"{start_str} to {end_str}",
            len(filtered),
            f"{total_hours:.1f}"
        ])

    print(f"  ✓ Report saved to: {filepath}")
    print()

def summary_report_all():
    print()
    print("  HOURS SUMMARY — ALL LEARNERS")
    print("-" * 40)
    start_dt, end_dt, start_str, end_str = get_date_range()

    records = load_attendance(start_dt, end_dt)

    if not records:
        print("  ⚠ No records found in this date range!")
        return

    # Aggregate by learner
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
        except ValueError:
            pass

    filename = f"summary_all_learners_{start_str}_to_{end_str}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    # Print to screen
    print()
    print("=" * 75)
    print(f"  {'Name':<28} {'Subprogram':<12} {'Grad Year':<12} {'Sessions':<10} {'Hours'}")
    print("-" * 75)
    for s in sorted(summary.values(), key=lambda x: x['name']):
        print(f"  {s['name']:<28} {s['subprogram']:<12} {s['grad_year']:<12} {s['sessions']:<10} {s['total_hours']:.1f}")
    print("=" * 75)
    print()

    # Save to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'subprogram', 'grad_year', 'sessions', 'total_hours'])
        for s in sorted(summary.values(), key=lambda x: x['name']):
            writer.writerow([s['name'], s['subprogram'], s['grad_year'], s['sessions'], f"{s['total_hours']:.1f}"])

    print(f"  ✓ Report saved to: {filepath}")
    print()

def summary_report_by_subprogram():
    print()
    print("  HOURS SUMMARY — BY SUB-PROGRAM")
    print("-" * 40)
    start_dt, end_dt, start_str, end_str = get_date_range()

    records = load_attendance(start_dt, end_dt)

    if not records:
        print("  ⚠ No records found in this date range!")
        return

    # Aggregate by learner first
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
        except ValueError:
            pass

    # Group by subprogram
    subprograms = {}
    for s in summary.values():
        sp = s['subprogram']
        if sp not in subprograms:
            subprograms[sp] = []
        subprograms[sp].append(s)

    filename = f"summary_by_subprogram_{start_str}_to_{end_str}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    rows_to_save = []

    # Print to screen
    for sp in sorted(subprograms.keys()):
        learners = sorted(subprograms[sp], key=lambda x: x['name'])
        print()
        print("=" * 75)
        print(f"  {sp}")
        print("=" * 75)
        print(f"  {'Name':<28} {'Grad Year':<12} {'Sessions':<10} {'Hours'}")
        print("-" * 75)
        sp_hours = 0.0
        for l in learners:
            print(f"  {l['name']:<28} {l['grad_year']:<12} {l['sessions']:<10} {l['total_hours']:.1f}")
            sp_hours += l['total_hours']
            rows_to_save.append([sp, l['name'], l['grad_year'], l['sessions'], f"{l['total_hours']:.1f}"])
        print("-" * 75)
        print(f"  {'Sub-program Total':<28} {'':12} {'':10} {sp_hours:.1f}")

    print()

    # Save to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['subprogram', 'name', 'grad_year', 'sessions', 'total_hours'])
        writer.writerows(rows_to_save)

    print(f"  ✓ Report saved to: {filepath}")
    print()

def batch_login_from_list():
    print()
    print("  BATCH LOGIN — SELECT FROM LIST")
    print("-" * 40)

    # Session type
    print("  Session type:")
    print("  1. Conference")
    print("  2. Journal Club")
    session_choice = input("  Select: ").strip()
    session_type = "Journal Club" if session_choice == "2" else "Conference"

    # Date and time
    while True:
        try:
            date_str = input("  Date (MM/DD/YYYY): ").strip()
            time_str = input("  Time (HH:MM AM/PM, e.g. 08:00 AM): ").strip().upper()
            datetime.strptime(date_str, '%m/%d/%Y')
            datetime.strptime(time_str, '%I:%M %p')
            break
        except ValueError:
            print("  ⚠ Invalid date or time format — try again")

    # Calculate hours
    time_obj = datetime.strptime(time_str, '%I:%M %p')
    if session_type == "Journal Club":
        hours_credited = "Journal Club"
    else:
        hours_credited = str(max(0, min(5, 5 - (time_obj.hour - 8))))

    # Load roster and display
    roster = load_roster()
    active = [r for r in roster if r['status'] == 'active']
    active_sorted = sorted(active, key=lambda x: x['name'])

    print()
    print("  Select learners (enter numbers separated by commas, e.g. 1,3,5):")
    print(f"  {'#':<5} {'Name':<30} {'Subprogram':<12} {'Grad Year'}")
    print("-" * 60)
    for i, r in enumerate(active_sorted, start=1):
        print(f"  {i:<5} {r['name']:<30} {r['subprogram']:<12} {r['grad_year']}")

    selections = input("\n  Enter numbers: ").strip()
    try:
        indices = [int(x.strip()) - 1 for x in selections.split(',')]
        selected = [active_sorted[i] for i in indices if 0 <= i < len(active_sorted)]
    except ValueError:
        print("  ⚠ Invalid selection")
        return

    if not selected:
        print("  ⚠ No learners selected")
        return

    # Review
    print()
    print("=" * 60)
    print(f"  Session:  {session_type}")
    print(f"  Date:     {date_str}")
    print(f"  Time:     {time_str}")
    print(f"  Hours:    {hours_credited}")
    print(f"  Learners: {len(selected)}")
    print("-" * 60)
    for r in selected:
        print(f"  {r['name']}")
    print("=" * 60)

    confirm = input("\n  Submit this batch? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("  Cancelled.")
        return

    # Log each person
    _process_batch(selected, date_str, time_str, hours_credited)

def batch_login_autofill():
    print()
    print("  BATCH LOGIN — TYPE NAMES WITH AUTOFILL")
    print("  Type first few letters of a name, select from matches.")
    print("  Type 'done' when finished.")
    print("-" * 40)

    # Session type
    print("  Session type:")
    print("  1. Conference")
    print("  2. Journal Club")
    session_choice = input("  Select: ").strip()
    session_type = "Journal Club" if session_choice == "2" else "Conference"

    # Date and time
    while True:
        try:
            date_str = input("  Date (MM/DD/YYYY): ").strip()
            time_str = input("  Time (HH:MM AM/PM, e.g. 08:00 AM): ").strip().upper()
            datetime.strptime(date_str, '%m/%d/%Y')
            datetime.strptime(time_str, '%I:%M %p')
            break
        except ValueError:
            print("  ⚠ Invalid date or time format — try again")

    # Calculate hours
    time_obj = datetime.strptime(time_str, '%I:%M %p')
    if session_type == "Journal Club":
        hours_credited = "Journal Club"
    else:
        hours_credited = str(max(0, min(5, 5 - (time_obj.hour - 8))))

    roster = load_roster()
    active = [r for r in roster if r['status'] == 'active']
    selected = []

    while True:
        search = input("\n  Type name (or 'done'): ").strip().lower()
        if search == 'done':
            break

        matches = [r for r in active if search in r['name'].lower()]

        if not matches:
            print("  ⚠ No matches found — try again")
            continue

        if len(matches) == 1:
            learner = matches[0]
            if any(s['badge_id'] == learner['badge_id'] for s in selected):
                print(f"  ⚠ {learner['name']} already in batch — skipping")
                continue
            selected.append(learner)
            print(f"  ✓ Added: {learner['name']}")
        else:
            print("  Matches found:")
            for i, r in enumerate(matches, start=1):
                print(f"  {i}. {r['name']} ({r['subprogram']})")
            try:
                choice = int(input("  Select number: ")) - 1
                learner = matches[choice]
                if any(s['badge_id'] == learner['badge_id'] for s in selected):
                    print(f"  ⚠ {learner['name']} already in batch — skipping")
                    continue
                selected.append(learner)
                print(f"  ✓ Added: {learner['name']}")
            except (ValueError, IndexError):
                print("  ⚠ Invalid selection — try again")

    if not selected:
        print("  ⚠ No learners selected")
        return

    # Review
    print()
    print("=" * 60)
    print(f"  Session:  {session_type}")
    print(f"  Date:     {date_str}")
    print(f"  Time:     {time_str}")
    print(f"  Hours:    {hours_credited}")
    print(f"  Learners: {len(selected)}")
    print("-" * 60)
    for r in selected:
        print(f"  {r['name']}")
    print("=" * 60)

    confirm = input("\n  Submit this batch? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("  Cancelled.")
        return

    _process_batch(selected, date_str, time_str, hours_credited)

def _process_batch(selected, date_str, time_str, hours_credited):
    logged = 0
    skipped = 0

    for learner in selected:
        # Check for duplicate
        duplicate = False
        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['badge_id'].strip() == learner['badge_id'] and row['date'].strip() == date_str:
                        duplicate = True
                        break

        if duplicate:
            print(f"\n  ⚠ {learner['name']} already has an entry for {date_str}")
            action = input("  Skip or add anyway? (skip/add): ").strip().lower()
            if action != 'add':
                skipped += 1
                print(f"  Skipped {learner['name']}")
                continue

        # Write to attendance log
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
                    date_str,
                    time_str,
                    learner['badge_id'],
                    learner['name'],
                    learner['status'],
                    learner['grad_year'],
                    learner['subprogram'],
                    hours_credited,
                    ''
                ])
            logged += 1
            print(f"  ✓ Logged: {learner['name']}")
        except Exception as e:
            print(f"  ✗ ERROR logging {learner['name']}: {e}")

    print()
    print("=" * 40)
    print(f"  Batch complete!")
    print(f"  ✓ Logged:  {logged}")
    print(f"  ✗ Skipped: {skipped}")
    print("=" * 40)
    print()

# ── MAIN MENU ─────────────────────────────────────────────────────────────────

def main():
    while True:
        print()
        print("=" * 50)
        print("  ATTENDANCE SYSTEM — SCHEDULE MANAGER")
        print("=" * 50)
        print()
        print("  ── ROSTER MANAGEMENT ──")
        print("  1.  Add a single learner")
        print("  2.  Batch add learners")
        print("  3.  Mark a single learner inactive")
        print("  4.  Batch mark learners inactive")
        print("  5.  View roster")
        print()
        print("  ── REPORTS ──")
        print("  6.  Detailed attendance - single learner")
        print("  7.  Detailed attendance - all learners")
        print("  8.  Hours summary - single learner")
        print("  9.  Hours summary - all learners")
        print("  10. Hours summary - by sub-program")
        print()
        print("  ── BATCH LOGIN ──")
        print("  11. Batch login - select from list")
        print("  12. Batch login - type with autofill")
        print()
        print("  ── EXIT ──")
        print("  13. Exit")
        print()

        choice = input("  Select an option: ").strip()

        if choice == '1':
            add_single_learner()
        elif choice == '2':
            batch_add_learners()
        elif choice == '3':
            mark_inactive_single()
        elif choice == '4':
            batch_mark_inactive()
        elif choice == '5':
            view_roster()
        elif choice == '6':
            detailed_report_single()
        elif choice == '7':
            detailed_report_all()
        elif choice == '8':
            summary_report_single()
        elif choice == '9':
            summary_report_all()
        elif choice == '10':
            summary_report_by_subprogram()
        elif choice == '11':
            batch_login_from_list()
        elif choice == '12':
            batch_login_autofill()
        elif choice == '13':
            print()
            print("  Goodbye!")
            break
        else:
            print("  ⚠ Invalid option — please enter a number 1-11")

if __name__ == "__main__":
    main()