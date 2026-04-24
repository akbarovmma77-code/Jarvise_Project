import os
import subprocess
import webbrowser

# ═══════════════════════════════════════════════
#  ПРОГРАММЫ
# ═══════════════════════════════════════════════
PROGRAMS = {
    "фортнайт":         "start com.epicgames.launcher:apps%3Afn%3Afortnite",
    "форт":             "start com.epicgames.launcher:apps%3Afn%3Afortnite",
    "гейм инсталлер":   r'"D:\GameInstallerPro\GameInstallerPro.exe"',
    "инсталлер":        r'"D:\GameInstallerPro\GameInstallerPro.exe"',
    "дискорд":          "start discord://",
    "спотифай":         "start spotify:",
    "роблокс":          "start roblox:",
    "обээс":            "start obs",
    "калькулятор":      "calc",
    "блокнот":          "notepad",
    "проводник":        "explorer",
    "диспетчер задач":  "taskmgr",
    "командную строку": "start cmd",
    "панель управления":"control",
    "настройки":        "start ms-settings:",
    "календарь":        "start outlookcal:",
    "камеру":           "start microsoft.windows.camera:",
    "ножницы":          "start snippingtool",
    "ворд":             "start winword",
    "эксель":           "start excel",
    "презентацию":      "start powerpnt",
    "презентации":      "start powerpnt",
    "браузер":          "start chrome",
    "хром":             "start chrome",
    "храм":             "start chrome",
    "оперу":            "start opera",
    "ютуб":             "start https://www.youtube.com",
    "почту":            "start https://mail.google.com",
    "телеграм":         "start tg://",
    "телегу":           "start tg://",
    "стим":             "start steam://open/main",
    "стин":             "start steam://open/main",
    "тим":              "start steam://open/main",
    "эпик геймс":       "start com.epicgames.launcher:",
    "код":              "code",
    "музыку":           "start mswindowsmusic:",
    "видео":            "start mswindowsvideo:",
    "фото":             "start mswindowsphotos:",
}

PROCESS_NAMES = {
    "дискорд":         "discord.exe",
    "спотифай":        "spotify.exe",
    "хром":            "chrome.exe",
    "браузер":         "chrome.exe",
    "опера":           "opera.exe",
    "оперу":           "opera.exe",
    "стим":            "steam.exe",
    "обс":             "obs64.exe",
    "обээс":           "obs64.exe",
    "телеграм":        "telegram.exe",
    "телегу":          "telegram.exe",
    "ворд":            "winword.exe",
    "эксель":          "excel.exe",
    "презентацию":     "powerpnt.exe",
    "презентации":     "powerpnt.exe",
    "код":             "code.exe",
    "роблокс":         "robloxplayerbeta.exe",
}


# ═══════════════════════════════════════════════
#  1. ОТКРЫТИЕ ПРИЛОЖЕНИЙ
# ═══════════════════════════════════════════════

def open_app(text: str) -> str | None:
    text = text.lower().strip()
    triggers = ["открой", "запусти", "включи", "запускай"]
    if not any(w in text for w in triggers):
        return None
    for name, cmd in PROGRAMS.items():
        if name in text:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"Поняла, открываю {name}."
            except Exception:
                return f"Сэр, не удалось запустить {name}."
    return None


# ═══════════════════════════════════════════════
#  2. ЗАКРЫТИЕ ПРИЛОЖЕНИЙ
# ═══════════════════════════════════════════════

def close_app(text: str) -> str | None:
    text = text.lower().strip()
    triggers = ["закрой", "выключи", "убей", "вырубай", "вырубить"]
    if not any(w in text for w in triggers):
        return None
    for name, proc in PROCESS_NAMES.items():
        if name in text:
            try:
                subprocess.Popen(f"taskkill /f /im {proc}", shell=True)
                return f"Сэр, закрываю {name}."
            except Exception:
                return f"Сэр, не удалось закрыть {name}."
    return None


# ═══════════════════════════════════════════════
#  3. ПОИСК В ИНТЕРНЕТЕ
# ═══════════════════════════════════════════════

def search_web(text: str) -> str | None:
    text = text.lower().strip()
    if "найди в интернете" not in text:
        return None
    query = text.replace("найди в интернете", "").strip()
    if not query:
        return "Сэр, уточните что искать."
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Ищу «{query}» в Google."
    except Exception:
        return "Сэр, не удалось открыть браузер."


# ═══════════════════════════════════════════════
#  4. ГРОМКОСТЬ  (PowerShell WScript.Shell — без сторонних утилит)
# ═══════════════════════════════════════════════

def _send_vol_key(char_code: int, repeat: int = 5) -> None:
    """
    Отправляет мультимедиа-клавишу через PowerShell.
    char_code:
        175 — VK_VOLUME_UP   (громче)
        174 — VK_VOLUME_DOWN (тише)
        173 — VK_VOLUME_MUTE (mute toggle)
    repeat: сколько раз нажать (каждое нажатие ≈ 2% громкости)
    """
    keys_expr = " ".join([f"[char]{char_code}"] * repeat)
    ps_cmd = (
        "$s = New-Object -ComObject WScript.Shell; "
        + "; ".join([f"$s.SendKeys([char]{char_code})"] * repeat)
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def system_control(text: str) -> str | None:
    """
    Управляет громкостью через PowerShell SendKeys.
    Триггеры: громче, тише, выключи звук, включи звук, без звука, верни звук.
    """
    text = text.lower().strip()

    if "громче" in text:
        try:
            _send_vol_key(175, repeat=5)
            return "Сэр, увеличиваю громкость."
        except Exception as e:
            return f"Сэр, ошибка громкости: {e}"

    if "тише" in text:
        try:
            _send_vol_key(174, repeat=5)
            return "Сэр, уменьшаю громкость."
        except Exception as e:
            return f"Сэр, ошибка громкости: {e}"

    if "выключи звук" in text or "без звука" in text:
        try:
            _send_vol_key(173, repeat=1)
            return "Сэр, звук выключен."
        except Exception as e:
            return f"Сэр, ошибка: {e}"

    if "включи звук" in text or "верни звук" in text:
        try:
            _send_vol_key(173, repeat=1)   # повторный toggle снимает mute
            return "Сэр, звук включён."
        except Exception as e:
            return f"Сэр, ошибка: {e}"

    return None


# ═══════════════════════════════════════════════
#  ГЛАВНЫЙ ФИЛЬТР ПК
# ═══════════════════════════════════════════════

def filter_pc(text: str) -> str | None:
    for fn in (open_app, close_app, search_web, system_control):
        res = fn(text)
        if res:
            return res
    return None