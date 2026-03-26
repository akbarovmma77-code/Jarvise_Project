import os
import subprocess
import webbrowser


# --- КОМАНДЫ ОТКРЫТИЯ ---
PROGRAMS = {
    "фортнайт": "start com.epicgames.launcher:apps%3Afn%3Afortnite",
    "форт": "start com.epicgames.launcher:apps%3Afn%3Afortnite",
    "гейм инсталлер": r'"D:\GameInstallerPro\GameInstallerPro.exe"',
    "инсталлер": r'"D:\GameInstallerPro\GameInstallerPro.exe"',
    "дискорд": "start discord://",
    "спотифай": "start spotify:",
    "роблокс": "start roblox:",
    "обээс": "start obs",
    "калькулятор": "calc",
    "блокнот": "notepad",
    "проводник": "explorer",
    "диспетчер задач": "taskmgr",
    "командную строку": "start cmd",
    "панель управления": "control",
    "настройки": "start ms-settings:",
    "календарь": "start outlookcal:",
    "камеру": "start microsoft.windows.camera:",
    "ножницы": "start snippingtool",
    "ворд": "start winword",
    "эксель": "start excel",
    "презентацию": "start powerpnt",
    "презентации": "start powerpnt",
    "браузер": "start chrome", 
    "хром": "start chrome",
    "храм": "start chrome",
    "оперу": "start opera",
    "ютуб": "start https://www.youtube.com",
    "почту": "start https://mail.google.com",
    "телеграм": "start tg://",
    "телегу": "start tg://",
    "стим": "start steam://open/main",
    "стин": "start steam://open/main",
    "тим": "start steam://open/main",
    "эпик геймс": "start com.epicgames.launcher:",
    "код": "code",
    "музыку": "start mswindowsmusic:",
    "видео": "start mswindowsvideo:",
    "фото": "start mswindowsphotos:"
}



def open_app(text):
    text = text.lower()
    # Добавил больше вариантов команд
    triggers = ["открой", "запусти", "включи", "запускай"]
    
    if any(word in text for word in triggers):
        for name, cmd in PROGRAMS.items():
            if name in text:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Поняла, открываю {name}."
                except:
                    return f"Сэр, не удалось запустить {name}."
    return None


def search_web(text):
    text = text.lower()
    if "найди в интернете" in text:
        query = text.replace("найди в интернете", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Ищу {query} в Google."
    return None
