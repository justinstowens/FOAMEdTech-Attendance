# FOAMEdTech Attendance System

**Free Open Access Medical Education Technology**

A professional badge reader attendance tracking system designed for medical education residency programs. Built by a physician, for physicians — no IT department required, no charge.

---

## What It Does

- Automatically captures badge swipes with accurate timestamps
- Tracks attendance hours based on arrival time down to the minute
- Supports multiple session types (Conference, Journal Club, Sim Lab sessions or unique sessions you create)
- Faculty role tracking with customizable role options -- Faculty can "badge in" too
- Generates detailed attendance reports exportable to CSV which is openable by excel
- Fully customizable for any residency program

---

## What You Need

Before installing, make sure you have the following:

### Hardware
- **A Windows-based computer** — must be running full Windows 10 or Windows 11 (not Windows SE or S Mode). Can be a mini PC, laptop, or touch-screen tablet. Must NOT be locked down by hospital IT — you need to be able to install software on it. Check that whatever you are using for this is actually running true Windows 10 or 11.  Chromebooks, Android Tablets, and Mac operating systems are not yet supported.
- **A badge reader or barcode scanner** — must be an HID (Human Interface Device) type reader that acts like a keyboard when it scans. Almost all standard badge readers and USB barcode scanners work this way. Your hosptial's IT department likely has these for use. The one I'm currently using is by Zebra and is available on Amazon for about $50. It is a "1D/2D" scanner.
- **A monitor, keyboard, or touch screen** — the system is designed to work with touch screens for the best experience, but a mouse works fine too. A window's based laptop works fine. One with a touch screen is a bonus. 
- **Speakers or audio output** — optional but recommended. The system plays distinct audio tones for successful scans, unknown badges, and duplicates. Some barcode scanners make their own sounds (mine does) so I leave the computer audio off. 
- **A USB drive** — for exporting attendance reports to your administrative assistant.

### Software
- **Microsoft Excel** — needed by your administrative assistant to open the CSV report files. Not required on the badge reader computer itself. We do our math for attendance % in excel.  Every program will calculate their own "denominator" differently. Some will require attendance when off service, some won't. Due to these differences, this version of the program does not have the math baked in. Maybe the next version ;)
- **Python 3.x** — the installer will attempt to install required Python libraries automatically, Including Python3.x.  It should install this on the computer as well.  If this installation fails, Python is free and can be downloaded manually from python.org.
- **Internet connection** — required during installation to download the system scripts from GitHub. Not required after installation.

---

## Installation

1. Download `FOAMEdTech_Attendance_Installer.exe` from the latest release
2. Run the installer on your Windows computer that you'll be connecting to the badge reader
3. When Windows shows a security warning, click **More info** then **Run anyway** — this is normal for new software
4. Follow the setup wizard — it takes about 5 minutes
5. Done! The system will start automatically every time the computer logs in

---

## Getting Help

Created by **J. Stowens MD**
📧 justinstowens@gmail.com

If you are using this system at your institution or have questions, feel free to reach out. This is a FOAMEd project — free and open access for the medical education community. Feedback always welcome :)

---

## What is FOAMEdTech?

**FOAMEd** stands for Free Open Access Medical Education — a movement by medical educators to share knowledge without paywalls. **FOAMEdTech** extends this philosophy to technology: using modern tools like AI to make useful software accessible to all medical educators, regardless of their technical background.  All coding for this project was done with assistance from Claude AI. The human involved had limited programming skills -- 2 classes, 25 years ago in highschool and a college class that he mainly skipped...

JS
