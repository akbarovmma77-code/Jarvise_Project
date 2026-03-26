import torch
import sounddevice as sd
import time
import os

# --- ИНИЦИАЛИЗАЦИЯ НЕЙРО-ГОЛОСА (Silero) ---
language = 'ru'
model_id = 'v4_ru'
device = torch.device('cpu') # Твой i5-13400 справится мгновенно

# Загружаем модель один раз при старте
model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)
model.to(device)

def va_speak(text):
    # 1. Очистка текста от символов разметки нейросети
    clean_text = text.replace("*", "").replace("#", "").strip()
    
    print(f"Ванесса: {clean_text}")
    
    # 2. Настройки голоса
    speaker = 'xenia' # Элегантный женский голос
    sample_rate = 48000
    
    try:
        # Генерируем аудио волну прямо в память
        audio = model.apply_tts(text=clean_text,
                                speaker=speaker,
                                sample_rate=sample_rate)
        
        # 3. Воспроизводим через динамики HP Victus
        sd.play(audio, sample_rate)
        # Ждем завершения фразы, чтобы звук не обрывался
        time.sleep(len(audio) / sample_rate + 0.3)
        sd.stop()
        
    except Exception as e:
        print(f"Ошибка нейро-голоса: {e}")

# Исправленная строка запуска
if __name__ == "__main__":
    va_speak("Тест нейронной системы пройден, сэр. Теперь мой голос звучит намного естественнее.")