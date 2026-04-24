import queue
import sys
import json

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ──────────────────────────────────────────────
# ЗАГРУЗКА МОДЕЛИ — print() здесь нужны,
# чтобы видеть прогресс в терминале при старте
# ──────────────────────────────────────────────

print("--- Загрузка модели (1.5 ГБ)... Подождите ---")
try:
    model = Model("models")
    print("--- МОДЕЛЬ ЗАГРУЖЕНА УСПЕШНО! ---")
except Exception as e:
    print(f"--- ОШИБКА: Не удалось загрузить модель! {e}")
    sys.exit(1)

# ──────────────────────────────────────────────
# АУДИО ОЧЕРЕДЬ
# ──────────────────────────────────────────────

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# ──────────────────────────────────────────────
# КОНСТАНТЫ
# ──────────────────────────────────────────────

EXIT_WORDS = {"стоп", "выход", "пока", "хватит", "отбой"}

# ──────────────────────────────────────────────
# ОСНОВНАЯ ФУНКЦИЯ — твой оригинальный алгоритм
# print() убраны только здесь — вместо них
# статусы идут в Streamlit чат через result_q
# ──────────────────────────────────────────────

def listen():
    """
    Слушает микрофон бесконечно.

    Алгоритм (оригинальный):
      • Ждёт фразу с «Ванесса».
      • Если «Ванесса привет» — возвращает «привет».
      • Если только «Ванесса» — ждёт следующую фразу как команду.

    Возвращает строку команды (без слова «Ванесса»).
    Без print() внутри — статусы идут в Streamlit через очередь.
    """
    samplerate = 16000

    # Очищаем старые данные в очереди
    while not q.empty():
        q.get()

    with sd.RawInputStream(
        samplerate=samplerate, blocksize=8000,
        device=None, dtype='int16', channels=1,
        callback=callback,
    ):
        rec = KaldiRecognizer(model, samplerate)
        waiting_for_command = False  # True = «Ванесса» услышана, ждём команду

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '').lower().strip()

                if not text:
                    continue

                if not waiting_for_command:
                    # ── Ждём «Ванесса» ───────────────────────────────────
                    if "ванесса" in text:
                        command = text.replace("ванесса", "").strip()
                        if command:
                            # «Ванесса открой браузер» — команда уже есть
                            return command
                        else:
                            # Только «Ванесса» — ждём следующую фразу
                            waiting_for_command = True
                else:
                    # ── Получаем команду после «Ванесса» ────────────────
                    return text


def is_exit_command(text: str) -> bool:
    """True если команда означает остановку."""
    if not text:
        return False
    return bool(set(text.lower().strip().split()) & EXIT_WORDS)