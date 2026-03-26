import stt    # Твой файл stt.py (слух)
import tts    # Твой файл tts.py (голос)
import brain  # Твой файл brain.py (мозг)
import skills # Твой файл skills.py (команды)

def start_vanessa():
    print("--- [СИСТЕМА] Ванесса загружена и готова к работе ---")
    
    # Стартовое приветствие
    tts.va_speak("Я на связи, сэр. Система полностью активирована.")

    while True:
        # 1. Слушаем микрофон
        user_text = stt.listen() 
        
        if not user_text:
            continue

        user_text = user_text.lower()
        print(f"Вы сказали: {user_text}")

        # 2. Проверка команд на выход
        if any(word in user_text for word in ["выход", "стоп", "отключись", "пока"]):
            tts.va_speak("Конечно, сэр. Перехожу в режим сна.")
            break

        # 3. --- БЛОК СКИЛЛОВ (КОМАНДЫ) ---
        # Проверяем, есть ли в тексте команда открыть программу
        command_res = skills.open_app(user_text)
        
        # Если не программа, проверяем поиск в интернете
        if not command_res:
            command_res = skills.search_web(user_text)

        # Если скилл сработал (вернул текст), озвучиваем и пропускаем нейросеть
        if command_res:
            print(f"Выполнена команда: {command_res}")
            tts.va_speak(command_res)
            continue 

        # 4. --- БЛОК НЕЙРОСЕТИ (ДИАЛОГ) ---
        # Если это не команда, отправляем текст в Gemma
        print("Ванесса думает...")
        answer = brain.get_answer(user_text)
        print(f"Ванесса ответила: {answer}")

        # Озвучиваем ответ
        tts.va_speak(answer)

# Исправленная точка входа с двойными подчеркиваниями
if __name__ == "__main__":
    start_vanessa()