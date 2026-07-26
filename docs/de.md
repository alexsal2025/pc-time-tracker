# PC Time Tracker

Leichtgewichtiger Zeiterfassungstool für Windows. Zählt, wie lange du am PC arbeitest, mit automatischer Pause bei Inaktivität, konfigurierbarem Tagesziel und Verlauf der letzten 7 Tage.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Funktionen

- 🕒 Großer Timer für die aktuelle Sitzung + Tagessumme
- ⏸ Schaltflächen **Start / Pause / Zurücksetzen**
- 😴 **Automatische Pause** bei Inaktivität — Schwellenwert einstellbar (10…3600 s)
- 🎯 Konfigurierbares **Tagesziel** (1–24 h) mit Fortschrittsbalken
- 📊 **7-Tage-Verlauf** mit Fortschrittsbalken pro Tag
- 🪟 „Immer im Vordergrund"-Option
- 💾 Automatisches Speichern alle 10 Sekunden und beim Schließen — Sitzungen überstehen einen Neustart
- 🎨 Dunkles Design, Schriftarten Consolas / Segoe UI
- 🌐 **10 Oberflächensprachen** — English (Standard), Русский, 中文, Español, Français, Deutsch, Português, 日本語, 한국어, العربية

## Screenshot

![PC Time Tracker](screenshots/de.png)

## Installation und Start

Benötigt **Python 3.10+** mit dem Modul `tkinter` (unter Windows standardmäßig enthalten).

```bash
python src/pc_time_tracker.py
```

Ein Doppelklick funktioniert ebenfalls, sofern `.py` mit Python verknüpft ist.

## Wo werden die Daten gespeichert

Alle Einstellungen und der Verlauf liegen in einer einzigen JSON-Datei:

```
%APPDATA%\PCTimeTracker\data.json
```

## Lizenz

MIT
