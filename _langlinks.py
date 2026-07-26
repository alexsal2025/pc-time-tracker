"""Превращает список языков в README в ссылки на соответствующие README,
и удаляет page.html из проекта и из git."""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\onefan1\.minimax\workspace\pc_time_tracker")

LANG_LINKS = [
    ("English (default)", "README.md"),
    ("Русский",            "docs/ru.md"),
    ("中文",                "docs/zh.md"),
    ("Español",            "docs/es.md"),
    ("Français",           "docs/fr.md"),
    ("Deutsch",            "docs/de.md"),
    ("Português",          "docs/pt.md"),
    ("日本語",              "docs/ja.md"),
    ("한국어",              "docs/ko.md"),
    ("العربية",            "docs/ar.md"),
]

# Главный README: ссылки относительно корня репо
ROOT_LINK = " — " + ", ".join(f"[{name}]({path})" for name, path in LANG_LINKS)
# В docs/<lang>.md: ссылки относительно docs/ (./<lang>.md)
DOCS_LINK = " — " + ", ".join(f"[{name}](./{Path(path).name})" for name, path in LANG_LINKS)

# Универсальный паттерн: строка, начинающаяся с маркера "10 ... languages" / "10 языков" и т.д.
# Берём только префикс до " — " и заменяем всю строку целиком.
PATTERN = re.compile(
    r"^(\s*-\s+\S+\s+\*\*[^*]*?10[^*]*?\*\*)\s+—\s+.*$",
    re.MULTILINE,
)

def replace_in(text: str, new_link: str) -> str:
    """Ищет в тексте строку, начинающуюся с '- <emoji> **10 ... ** — <список>',
    и заменяет её на '<тот же префикс><new_link>'."""
    def sub(m):
        prefix = m.group(1)  # всё до " — "
        return prefix + new_link
    return PATTERN.sub(sub, text)

# Главный README
readme = ROOT / "README.md"
if readme.exists():
    txt = readme.read_text(encoding="utf-8")
    new = replace_in(txt, ROOT_LINK)
    if new != txt:
        readme.write_text(new, encoding="utf-8")
        print("  updated README.md")
    else:
        print("  WARN: no change in README.md")

# docs/*.md
for lang_file in ROOT.glob("docs/*.md"):
    txt = lang_file.read_text(encoding="utf-8")
    new = replace_in(txt, DOCS_LINK)
    if new != txt:
        lang_file.write_text(new, encoding="utf-8")
        print(f"  updated docs/{lang_file.name}")
    else:
        print(f"  WARN: no change in docs/{lang_file.name}")
