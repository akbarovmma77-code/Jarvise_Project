import ollama
import pandas as pd
import io
import contextlib
 

# Загружаем данные (укажи свой путь к CSV)
try:
    df = pd.read_csv("data.csv")
    df_info = f"Доступны столбцы: {list(df.columns)}"
except:
    df = None
    df_info = "Данные пока не загружены."

# История сообщений
messages = [
    {
        'role': 'system', 
        'content': f"""Ты — Ванесса, высокотехнологичный ИИ-аналитик. 
        Твои правила:
        1. Если сэр просто общается (приветствие, вопросы о делах), отвечай как вежливый ассистент БЕЗ использования тегов [CODE].
        2. Если сэр просит анализ данных, расчеты или графики, используй данные из df ({df_info}).
        3. Код для анализа ПИШИ СТРОГО внутри тегов [CODE]...[/CODE]. 
        4. Внутри [CODE] должен быть только чистый Python-код, пригодный для функции exec().
        5. Всегда называй пользователя 'сэр'."""
    }
]

def execute_python(code):
    """Выполняет код и возвращает результат или график"""
    global df
    # Создаем буфер для перехвата текста из print()
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            # Импорты внутри exec, чтобы код от Gemma работал
            exec_globals = {'df': df, 'pd': pd, 'plt': __import__('matplotlib.pyplot')}
            exec(code, exec_globals)
        except Exception as e:
            return f"Ошибка в коде: {e}"
    return f.getvalue() or "Код выполнен успешно."
def get_answer(query):
    global messages
    messages.append({'role': 'user', 'content': query})
    
    try:
        response = ollama.chat(model='gemma3:4b', messages=messages)
        answer = response['message']['content']
        
        # Проверяем, есть ли РЕАЛЬНЫЙ код внутри тегов
        if "[CODE]" in answer:
            start = answer.find("[CODE]") + 6
            end = answer.find("[/CODE]")
            if end == -1: end = len(answer)
            
            code = answer[start:end].strip()
            
            # Добавим проверку: если внутри "кода" обычные слова без команд Python, не выполняем
            if "df" in code or "plt" in code or "pd" in code or "print" in code:
                print(f"--- Ванесса пишет код ---\n{code}")
                result = execute_python(code)
                # Убираем теги из ответа для красоты и добавляем результат
                clean_answer = answer.replace(f"[CODE]{code}[/CODE]", "").strip()
                final_output = f"{clean_answer}\n[Результат анализа: {result}]"
            else:
                # Если модель ошиблась и засунула текст в [CODE]
                final_output = code 
        else:
            final_output = answer

        messages.append({'role': 'assistant', 'content': final_output})
        return final_output
        
    except Exception as e:
        return f"Ошибка связи с ядром: {e}"
        
    except Exception as e:
        return f"Ошибка связи с ядром: {e}"

if __name__ == "__main__":
    # Тест активации
    print("Ванесса: Слушаю, сэр.")
    print(get_answer("Ванесса, покажи среднее значение в первом столбце"))