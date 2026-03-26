import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Проверка и загрузка модели
print("--- Загрузка средней модели (1.5 ГБ)... Подождите пару секунд ---")
try:
    model = Model("models") 
    print("--- МОДЕЛЬ ЗАГРУЖЕНА УСПЕШНО! ---")
except Exception as e:
    print(f"--- ОШИБКА: Не удалось найти файлы модели! Ошибка: {e}")
    sys.exit()

def listen():
    samplerate = 16000 
    
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, 
                            dtype='int16', channels=1, callback=callback):
        
        rec = KaldiRecognizer(model, samplerate)
        print(">>> ВАНЕССА В РЕЖИМЕ ОЖИДАНИЯ (скажи 'Ванесса')...")
        
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '').lower() # Переводим в нижний регистр
                
                # ПРОВЕРКА ИМЕНИ
                if "ванесса" in text:
                    # Очищаем команду: убираем само слово "ванесса"
                    command = text.replace("ванесса", "").strip()
                    
                    if command:
                        print(f"Поняла команду: {command}")
                        return command
                    else:
                        # Если сказал только имя, подтверждаем и слушаем дальше
                        print("Ванесса: Слушаю вас, сэр. Что нужно сделать?")
                        # Продолжаем цикл ожидания команды