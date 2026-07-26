"""
PC Time Tracker — простой контроллер времени за ПК.
Считает текущую сессию и дневной итог, автопаузится при бездействии,
помнит историю за последние 30 дней. Данные хранятся в JSON в профиле пользователя.
"""

import json
import os
import sys
import time
import ctypes
from datetime import datetime, date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Настройки ----------
IDLE_TIMEOUT_SEC = 300         # через сколько секунд без ввода — автопауза (5 мин)
IDLE_RESUME_SEC = 5            # при вводе в течение N сек — снимаем с паузы
UPDATE_INTERVAL_MS = 500       # как часто обновлять UI
SAVE_INTERVAL_SEC = 10         # как часто сохранять на диск
HISTORY_DAYS = 30              # сколько дней истории хранить
DEFAULT_GOAL_HOURS = 8         # цель дня по умолчанию
DEFAULT_LANG = "en"            # язык по умолчанию (English only)

# ---------- Переводы (только English) ----------
TRANSLATIONS = {
    "en": {
        "title_app": "PC Time Tracker",
        "current_session": "CURRENT SESSION",
        "today": "TODAY",
        "history": "HISTORY (7 days)",
        "start": "▶ Start",
        "pause": "⏸ Pause",
        "reset": "↺ Reset",
        "paused": "paused",
        "running": "counting",
        "auto_pause": "Auto-pause",
        "ontop": "Always on top",
        "timeout": "Idle timeout, sec:",
        "timeout_range": "(10…3600)",
        "goal": "Daily goal, h:",
        "goal_range": "(1…24)",
        "reset_title": "Reset",
        "reset_msg": "Reset the current session? (Today's total will be kept.)",
        "today_short": "today",
        "status_autopause": "autopause · idle {t}",
        "status_idle": "counting · idle {t}",
        "goal_suffix": " / {n} h",
        "history_total": "Σ {t}",
    },
}

LANG_CODES = ["en"]

# ---------- Пути ----------
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "PCTimeTracker"
APP_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = APP_DIR / "data.json"

# ---------- Windows API для определения бездействия ----------
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_seconds() -> float:
    """Сколько секунд прошло с последнего ввода (мышь/клавиатура)."""
    try:
        last_input = LASTINPUTINFO()
        last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input))
        tick = ctypes.windll.kernel32.GetTickCount()
        return (tick - last_input.dwTime) / 1000.0
    except Exception:
        return 0.0

# ---------- Хранилище ----------
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"days": {}, "last_session_start": None, "accumulated": 0}

def save_data(data: dict) -> None:
    # Чистим старую историю
    cutoff = (date.today() - timedelta(days=HISTORY_DAYS)).isoformat()
    data["days"] = {k: v for k, v in data["days"].items() if k >= cutoff}
    tmp = DATA_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(DATA_FILE)

# ---------- Форматирование ----------
def fmt(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def fmt_long(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h: parts.append(f"{h} ч")
    if m: parts.append(f"{m} мин")
    if not h and not m:
        parts.append(f"{s} сек")
    return " ".join(parts)

# ---------- Цвета (тёмная тема) ----------
BG = "#1e1e2e"
PANEL = "#28283c"
FG = "#e4e4f4"
MUTED = "#8a8aa3"
ACCENT = "#7aa2f7"
DANGER = "#f7768e"
GREEN = "#9ece6a"
YELLOW = "#e0af68"
BTN = "#3b3b54"
BTN_HOVER = "#4b4b6a"

# ---------- Приложение ----------
class TimeTracker:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.data = load_data()
        self.running = False
        self.idle_paused = False
        self.session_start_ts = None  # когда текущая сессия началась
        self.last_save_ts = 0.0
        self.idle_timeout_sec = self.data.get("idle_timeout_sec", IDLE_TIMEOUT_SEC)
        self.lang = self.data.get("lang", DEFAULT_LANG)
        if self.lang not in TRANSLATIONS:
            self.lang = DEFAULT_LANG
        self.goal_hours = max(1, min(24, int(self.data.get("goal_hours", DEFAULT_GOAL_HOURS))))

        # Восстанавливаем сессию, если она была активна при прошлом закрытии
        if self.data.get("last_session_start"):
            try:
                ts = self.data["last_session_start"]
                self.session_start_ts = ts
                self.running = True
            except Exception:
                self.session_start_ts = None
                self.running = False

        self.build_ui()
        self.tick()

    def build_ui(self):
        self.root.title(self.t("title_app"))
        self.root.configure(bg=BG)
        self.root.geometry("640x860")
        self.root.minsize(620, 820)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 10, "bold"))
        style.configure("Timer.TLabel", background=PANEL, foreground=ACCENT, font=("Consolas", 48, "bold"))
        style.configure("Small.Timer.TLabel", background=PANEL, foreground=MUTED, font=("Consolas", 18, "bold"))
        style.configure("Accent.Horizontal.TScale",
                        background=PANEL, troughcolor=BTN, sliderthickness=0)

        # Верх: текущая сессия
        top = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 16))
        top.pack(fill="x", padx=14, pady=(14, 8))

        self.session_title = ttk.Label(top, style="Title.TLabel")
        self.session_title.pack(anchor="w")
        self.session_label = ttk.Label(top, text="00:00", style="Timer.TLabel")
        self.session_label.pack(anchor="w", pady=(6, 0))
        self.status_label = ttk.Label(top, style="Muted.TLabel")
        self.status_label.configure(background=PANEL)
        self.status_label.pack(anchor="w", pady=(2, 0))

        # Сред: статистика дня
        mid = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 14))
        mid.pack(fill="x", padx=14, pady=4)

        self.today_title = ttk.Label(mid, style="Title.TLabel")
        self.today_title.pack(anchor="w")
        self.today_label = ttk.Label(mid, text="00:00:00", style="Small.Timer.TLabel")
        self.today_label.configure(foreground=GREEN)
        self.today_label.pack(anchor="w", pady=(4, 0))

        # Шкала прогресса дня
        prog_row = ttk.Frame(mid, style="Panel.TFrame")
        prog_row.pack(fill="x", pady=(8, 0))
        self.progress = ttk.Scale(prog_row, from_=0, to=self.goal_hours*3600,
                                  orient="horizontal",
                                  style="Accent.Horizontal.TScale", state="disabled")
        self.progress.pack(side="left", fill="x", expand=True)
        self.goal_label = ttk.Label(prog_row, style="Muted.TLabel")
        self.goal_label.configure(background=PANEL)
        self.goal_label.pack(side="left", padx=(8, 0))

        # Кнопки
        btns = ttk.Frame(self.root, style="TFrame")
        btns.pack(fill="x", padx=14, pady=12)

        self.start_btn = tk.Button(btns, command=self.toggle,
                                   bg=ACCENT, fg="#1a1a2e", activebackground="#8ab4ff",
                                   font=("Segoe UI", 13, "bold"), relief="flat",
                                   padx=20, pady=12, cursor="hand2", bd=0)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.reset_btn = tk.Button(btns, command=self.reset,
                                   bg=BTN, fg=FG, activebackground=BTN_HOVER,
                                   font=("Segoe UI", 13), relief="flat",
                                   padx=20, pady=12, cursor="hand2", bd=0)
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        # Чекбоксы
        opts = ttk.Frame(self.root, style="TFrame")
        opts.pack(fill="x", padx=14, pady=(0, 6))
        self.ontop_var = tk.BooleanVar(value=False)
        self.ontop_chk = tk.Checkbutton(opts, variable=self.ontop_var,
                                        command=self.toggle_ontop, bg=BG, fg=FG, selectcolor=BG,
                                        activebackground=BG, activeforeground=FG,
                                        font=("Segoe UI", 9))
        self.ontop_chk.pack(side="left")
        self.idle_var = tk.BooleanVar(value=True)
        self.idle_chk = tk.Checkbutton(opts, variable=self.idle_var,
                                       bg=BG, fg=FG, selectcolor=BG,
                                       activebackground=BG, activeforeground=FG,
                                       font=("Segoe UI", 9))
        self.idle_chk.pack(side="left", padx=(12, 0))

        # Таймаут автопаузы
        idle_row = ttk.Frame(self.root, style="TFrame")
        idle_row.pack(fill="x", padx=14, pady=(0, 6))
        self.timeout_lbl = tk.Label(idle_row, bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.timeout_lbl.pack(side="left")
        self.timeout_var = tk.IntVar(value=self.idle_timeout_sec)
        self.timeout_spin = tk.Spinbox(idle_row, from_=10, to=3600,
                                        increment=30, textvariable=self.timeout_var,
                                        width=6, bg=PANEL, fg=FG,
                                        buttonbackground=BTN,
                                        relief="flat", font=("Segoe UI", 9),
                                        insertbackground=FG)
        self.timeout_spin.pack(side="left", padx=(8, 0))
        self.timeout_spin.bind("<FocusOut>", lambda e: self.update_timeout())
        self.timeout_spin.bind("<Return>", lambda e: self.update_timeout())
        self.timeout_range_lbl = tk.Label(idle_row, bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.timeout_range_lbl.pack(side="left", padx=(6, 0))

        # Цель дня
        goal_row = ttk.Frame(self.root, style="TFrame")
        goal_row.pack(fill="x", padx=14, pady=(0, 10))
        self.goal_lbl = tk.Label(goal_row, bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.goal_lbl.pack(side="left")
        self.goal_var = tk.IntVar(value=self.goal_hours)
        self.goal_spin = tk.Spinbox(goal_row, from_=1, to=24,
                                     increment=1, textvariable=self.goal_var,
                                     width=6, bg=PANEL, fg=FG,
                                     buttonbackground=BTN,
                                     relief="flat", font=("Segoe UI", 9),
                                     insertbackground=FG)
        self.goal_spin.pack(side="left", padx=(8, 0))
        self.goal_spin.bind("<FocusOut>", lambda e: self.update_goal())
        self.goal_spin.bind("<Return>", lambda e: self.update_goal())
        self.goal_range_lbl = tk.Label(goal_row, bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.goal_range_lbl.pack(side="left", padx=(6, 0))

        # История
        bot = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 12))
        bot.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        hist_header = ttk.Frame(bot, style="Panel.TFrame")
        hist_header.pack(fill="x")
        self.history_title = ttk.Label(hist_header, style="Title.TLabel")
        self.history_title.pack(side="left")
        self.total_label = ttk.Label(hist_header, style="Muted.TLabel")
        self.total_label.configure(background=PANEL, foreground=YELLOW)
        self.total_label.pack(side="right")

        self.history_text = tk.Text(bot, height=12, bg="#1a1a28", fg=FG,
                                    font=("Consolas", 11), relief="flat",
                                    highlightthickness=0, padx=10, pady=10)
        self.history_text.pack(fill="both", expand=True, pady=(8, 0))
        self.history_text.configure(state="disabled")

        self.apply_language()
        self.refresh_buttons()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_language(self):
        """Обновляет все видимые надписи под текущий язык."""
        self.root.title(self.t("title_app"))
        self.session_title.configure(text=self.t("current_session"))
        self.today_title.configure(text=self.t("today"))
        self.history_title.configure(text=self.t("history"))
        self.ontop_chk.configure(text=self.t("ontop"))
        self.idle_chk.configure(text=self.t("auto_pause"))
        self.timeout_lbl.configure(text=self.t("timeout"))
        self.timeout_range_lbl.configure(text=self.t("timeout_range"))
        self.goal_lbl.configure(text=self.t("goal"))
        self.goal_range_lbl.configure(text=self.t("goal_range"))
        # Кнопка start/pause — текст зависит от состояния
        self.refresh_buttons()
        # Цель в правом углу шкалы
        self.goal_label.configure(text=self.t("goal_suffix", n=self.goal_hours))
        # Статус
        if not self.running:
            self.status_label.configure(text=self.t("paused"), foreground=MUTED)

    def toggle_ontop(self):
        self.root.attributes("-topmost", self.ontop_var.get())

    def update_timeout(self):
        try:
            v = max(10, min(3600, int(self.timeout_var.get())))
        except (ValueError, tk.TclError):
            v = IDLE_TIMEOUT_SEC
        self.timeout_var.set(v)
        self.idle_timeout_sec = v
        self.data["idle_timeout_sec"] = v
        self.save()

    def update_goal(self):
        try:
            v = max(1, min(24, int(self.goal_var.get())))
        except (ValueError, tk.TclError):
            v = DEFAULT_GOAL_HOURS
        self.goal_var.set(v)
        self.goal_hours = v
        self.data["goal_hours"] = v
        try:
            self.progress.configure(to=v * 3600)
        except tk.TclError:
            pass
        self.apply_language()
        self.save()

    def toggle(self):
        if self.running and not self.idle_paused:
            self.pause()
        else:
            self.start()

    def start(self):
        if not self.running:
            self.running = True
            self.idle_paused = False
            self.session_start_ts = time.time()
            self.data["last_session_start"] = self.session_start_ts
        else:
            # снимаем с idle-паузы
            self.idle_paused = False
            self.session_start_ts = time.time()
        self.refresh_buttons()
        self.save()

    def pause(self):
        if self.running and self.session_start_ts:
            self.commit_session()
        self.running = False
        self.idle_paused = False
        self.session_start_ts = None
        self.data["last_session_start"] = None
        self.refresh_buttons()
        self.save()

    def reset(self):
        if not messagebox.askyesno(self.t("reset_title"), self.t("reset_msg")):
            return
        self.session_start_ts = None
        if self.running:
            self.session_start_ts = time.time()
            self.data["last_session_start"] = self.session_start_ts
        self.refresh_buttons()
        self.save()

    def commit_session(self):
        if not self.session_start_ts:
            return
        elapsed = int(time.time() - self.session_start_ts)
        if elapsed <= 0:
            return
        today = date.today().isoformat()
        self.data["days"][today] = self.data["days"].get(today, 0) + elapsed
        self.session_start_ts = time.time()
        self.data["last_session_start"] = self.session_start_ts

    def tick(self):
        try:
            now = time.time()

            # Проверка бездействия
            idle = get_idle_seconds() if self.running else 0.0
            if self.running and self.idle_var.get() and not self.idle_paused:
                if idle > self.idle_timeout_sec:
                    # устойчиво бездействуем — пауза
                    self.idle_paused = True
                    if self.session_start_ts:
                        self.commit_session()
                    self.status_label.configure(
                        text=self.t("status_autopause", t=fmt_long(int(idle))),
                        foreground=YELLOW)

            # Снимаем с автопаузы, как только пользователь вернулся
            if self.idle_paused and idle < IDLE_RESUME_SEC:
                self.idle_paused = False
                self.session_start_ts = time.time()
                self.data["last_session_start"] = self.session_start_ts

            # Считаем текущую сессию
            session_sec = 0
            if self.running and self.session_start_ts and not self.idle_paused:
                session_sec = int(now - self.session_start_ts)

            # Считаем итог дня = уже сохранённое + текущая сессия
            today = date.today().isoformat()
            today_total = self.data["days"].get(today, 0) + session_sec

            # UI
            self.session_label.configure(text=fmt(session_sec) if session_sec else "00:00")
            self.today_label.configure(text=fmt(today_total))

            if not self.running:
                self.status_label.configure(text=self.t("paused"), foreground=MUTED)
            elif self.idle_paused:
                # уже выставили жёлтый при паузе
                pass
            else:
                # показываем простой, пока не дошли до порога
                if self.idle_var.get() and idle > 5:
                    self.status_label.configure(
                        text=self.t("status_idle", t=fmt_long(int(idle))),
                        foreground=FG)
                else:
                    self.status_label.configure(text=self.t("running"), foreground=GREEN)

            # Прогресс
            try:
                self.progress.configure(value=min(today_total, 8*3600))
            except tk.TclError:
                pass

            # История
            self.render_history()

            # Сохранение
            if now - self.last_save_ts > SAVE_INTERVAL_SEC:
                if self.running and self.session_start_ts and not self.idle_paused:
                    self.data["last_session_start"] = self.session_start_ts
                save_data(self.data)
                self.last_save_ts = now

        finally:
            self.root.after(UPDATE_INTERVAL_MS, self.tick)

    def render_history(self):
        today = date.today()
        lines = []
        max_sec = max(self.goal_hours * 3600, 1)
        for i in range(7):
            d = (today - timedelta(days=i)).isoformat()
            sec = self.data["days"].get(d, 0)
            if i == 0:
                label = self.t("today_short")
            else:
                # короткое название дня недели + дата
                wd_names_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                wd = wd_names_en[(today - timedelta(days=i)).weekday()]
                day = (today - timedelta(days=i)).day
                month = (today - timedelta(days=i)).month
                label = f"{wd} {day:02d}.{month:02d}"
            bar_len = int(min(sec, max_sec) / max_sec * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {label:<10} {bar} {fmt(sec)}")

        # Суммируем сохранённые дни (без текущей сессии)
        saved_total = sum(self.data["days"].get((today - timedelta(days=i)).isoformat(), 0)
                          for i in range(7))
        # плюс текущая активная сессия
        live = 0
        if self.running and self.session_start_ts and not self.idle_paused:
            live = int(time.time() - self.session_start_ts)
        total = saved_total + live

        self.total_label.configure(text=self.t("history_total", t=fmt(total)))

        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(lines))
        self.history_text.configure(state="disabled")

    def save(self):
        save_data(self.data)

    def t(self, key: str, **kwargs) -> str:
        """Получить строку на текущем языке с подстановкой {placeholders}."""
        s = TRANSLATIONS.get(self.lang, TRANSLATIONS[DEFAULT_LANG]).get(key, key)
        if kwargs:
            try:
                return s.format(**kwargs)
            except (KeyError, IndexError):
                return s
        return s

    def refresh_buttons(self):
        if self.running and not self.idle_paused:
            self.start_btn.configure(text=self.t("pause"), bg=YELLOW)
        else:
            self.start_btn.configure(text=self.t("start"), bg=ACCENT)
        self.reset_btn.configure(text=self.t("reset"))

    def on_close(self):
        if self.running and self.session_start_ts and not self.idle_paused:
            self.commit_session()
            self.data["last_session_start"] = self.session_start_ts
        else:
            self.data["last_session_start"] = None
        save_data(self.data)
        self.root.destroy()

def main():
    root = tk.Tk()
    TimeTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
