import torch
import sounddevice as sd
import time

# ──────────────────────────────────────────────
# ИНИЦИАЛИЗАЦИЯ МОДЕЛИ (один раз при старте)
# ──────────────────────────────────────────────

print("--- TTS: загрузка голосовой модели Silero... ---")
try:
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='v4_ru',
    )
    model.to(torch.device('cpu'))
    print("--- TTS: модель загружена успешно! ---")
except Exception as e:
    print(f"--- TTS ОШИБКА: {e}")
    model = None

# ──────────────────────────────────────────────
# ОЗВУЧКА
# ──────────────────────────────────────────────

def va_speak(text: str):
    if model is None:
        print("TTS: модель не загружена, озвучка недоступна.")
        return

    # Очищаем текст от символов разметки
    clean_text = text.replace("*", "").replace("#", "").strip()
    if not clean_text:
        return

    print(f"Ванесса: {clean_text}")

    try:
        # Генерируем аудио — apply_tts возвращает PyTorch тензор
        audio_tensor = model.apply_tts(
            text=clean_text,
            speaker='xenia',
            sample_rate=48000,
        )

        # ── ИСПРАВЛЕНИЕ 1 ──────────────────────────────────────────────
        # Конвертируем тензор в numpy — без этого sd.play() не воспроизводит звук
        audio_numpy = audio_tensor.numpy()

        # Останавливаем предыдущее воспроизведение если оно ещё идёт
        sd.stop()

        # ── ИСПРАВЛЕНИЕ 2 ──────────────────────────────────────────────
        # sd.wait() надёжнее time.sleep() — ждёт именно до конца аудио,
        # не зависит от длины фразы и не обрывает звук раньше времени
        sd.play(audio_numpy, samplerate=48000)
        sd.wait()

    except Exception as e:
        print(f"Ошибка нейро-голоса: {e}")

