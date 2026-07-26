# PC Time Tracker

Lightweight desktop time tracker for Windows. Counts how long you spend at the PC, with auto-pause on idle, configurable daily goal, and 7-day history.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🕒 Big current-session timer + daily total
- ⏸ **Start / Pause / Reset** buttons
- 😴 **Auto-pause** on idle — threshold adjustable (10…3600 sec)
- 🎯 Configurable **daily goal** (1–24 h) with a progress bar
- 📊 **7-day history** with progress bars per day
- 🪟 "Always on top" toggle
- 💾 Auto-save every 10 seconds and on close — sessions survive a reboot
- 🎨 Dark theme, Consolas/Segoe UI fonts
- 🇬🇧 English UI

## Screenshot

```
┌─ PC Time Tracker ───────────────────┐
│  CURRENT SESSION                    │
│  01:23:45                           │
│  counting · idle 8 sec              │
│                                     │
│  TODAY                              │
│  03:12:00   ▓▓▓▓▓▓░░░░░░░░░░ / 8 h  │
│                                     │
│      [▶ Start]      [↺ Reset]       │
│                                     │
│  [ ] Always on top   [✓] Auto-pause │
│  Idle timeout, sec:  [300] (10…3600)│
│  Daily goal, h:      [8]   (1…24)   │
│                                     │
│  HISTORY (7 days)            Σ 12:00 │
│  ...                                │
└─────────────────────────────────────┘
```

## Install & Run

Requires **Python 3.10+** with the `tkinter` module (included by default on Windows).

```bash
python pc_time_tracker.py
```

Double-click works too, if `.py` is associated with Python.

## Where data is stored

All settings and history live in a single JSON file:

```
%APPDATA%\PCTimeTracker\data.json
```

## License

MIT
