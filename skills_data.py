import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from transliterate import translit

# Seaborn (опционально)
try:
    import seaborn as sns
    _SNS_OK = True
except ImportError:
    _SNS_OK = False
    print("[Ванесса] seaborn не установлен. pip install seaborn")

# rapidfuzz — нечёткий поиск файлов и колонок
try:
    from rapidfuzz import fuzz as _fuzz, process as _fuzz_process
    _FUZZY_OK = True
except ImportError:
    _FUZZY_OK = False
    print("[Ванесса] rapidfuzz не установлен. pip install rapidfuzz")


# ═══════════════════════════════════════════════
#  КОНСТАНТЫ
# ═══════════════════════════════════════════════
USER_PATH    = os.path.expanduser("~")
SEARCH_DIRS  = [
    os.path.join(USER_PATH, "Desktop"),
    os.path.join(USER_PATH, "Documents"),
    os.path.join(USER_PATH, "Downloads"),
    os.getcwd(),
]
EXCLUDE_DIRS = [
    "site-packages", "dist-packages",
    "numpy", "scipy", "pandas",
    "__pycache__", ".git",
]
FUZZY_THRESHOLD = 70


# ═══════════════════════════════════════════════
#  ГЛОБАЛЬНЫЙ КОНТЕКСТ
# ═══════════════════════════════════════════════
_last_file:  str          | None = None
_current_df: pd.DataFrame | None = None

def get_last_file() -> str | None:
    return _last_file

def get_current_df() -> pd.DataFrame | None:
    return _current_df

def set_last_file(path: str | None) -> None:
    global _last_file, _current_df
    _last_file = path
    if path:
        try:
            _current_df = _load_df(path)
            if _current_df is None:
                raise ValueError("_load_df вернул None")
            print(f"[Ванесса] Загружен: {os.path.basename(path)} "
                  f"({_current_df.shape[0]}x{_current_df.shape[1]})")
        except Exception as e:
            _current_df = None
            print(f"[Ванесса] Не удалось загрузить DataFrame: {e}")
    else:
        _current_df = None


# ═══════════════════════════════════════════════
#  1. КОНВЕРТЕР ЧИСЕЛ: СЛОВА → ЦИФРЫ
# ═══════════════════════════════════════════════
_NUM_WORDS = {
    "ноль": 0, "нуль": 0,
    "один": 1, "одна": 1, "одно": 1,
    "два": 2, "две": 2,
    "три": 3, "четыре": 4, "пять": 5,
    "шесть": 6, "семь": 7, "восемь": 8,
    "девять": 9, "десять": 10,
    "одиннадцать": 11, "двенадцать": 12,
    "тринадцать": 13, "четырнадцать": 14,
    "пятнадцать": 15, "шестнадцать": 16,
    "семнадцать": 17, "восемнадцать": 18,
    "девятнадцать": 19, "двадцать": 20,
    "тридцать": 30, "сорок": 40,
    "пятьдесят": 50, "шестьдесят": 60,
    "семьдесят": 70, "восемьдесят": 80,
    "девяносто": 90, "сто": 100,
    "двести": 200, "триста": 300,
    "четыреста": 400, "пятьсот": 500,
    "шестьсот": 600, "семьсот": 700,
    "восемьсот": 800, "девятьсот": 900,
    "тысяча": 1000, "тысячи": 1000,
}

def text_to_numeric(text: str) -> str:
    """«фильтруй меньше пятьдесят» → «фильтруй меньше 50»"""
    words = text.lower().split()
    result, i = [], 0
    while i < len(words):
        if words[i] in _NUM_WORDS:
            val = _NUM_WORDS[words[i]]
            if i + 1 < len(words) and words[i + 1] in _NUM_WORDS:
                next_val = _NUM_WORDS[words[i + 1]]
                if val >= 20 and 1 <= next_val <= 9:
                    result.append(str(val + next_val))
                    i += 2
                    continue
            result.append(str(val))
        else:
            result.append(words[i])
        i += 1
    return " ".join(result)


# ═══════════════════════════════════════════════
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════

def _normalize(text: str) -> str:
    return text.strip().lower()

def _variants(name: str) -> list[str]:
    name = _normalize(name).replace(".csv", "").strip()
    candidates = [name]
    try:
        candidates.append(translit(name, "ru", reversed=True))
    except Exception:
        pass
    try:
        candidates.append(translit(name, "ru"))
    except Exception:
        pass
    return list(dict.fromkeys(candidates))

def _is_match(spoken: str, file_stem: str) -> bool:
    variants = _variants(spoken)
    if any(v in file_stem or file_stem in v for v in variants):
        return True
    if _FUZZY_OK:
        for v in variants:
            score = _fuzz.ratio(v, file_stem)
            print(f"[Ванесса] fuzzy: «{v}» vs «{file_stem}» = {score:.0f}%")
            if score >= FUZZY_THRESHOLD:
                return True
    return False

def _load_df(path: str) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, sep=None, engine='python', encoding='utf-8-sig')

        # ФИКС СМЕЩЕНИЯ
        if not df.empty:
            first_row_values = [str(val).lower() for val in df.iloc[0].values]
            if any(word in first_row_values for word in ['sn', 'pclass', 'survived', 'gender']):
                print("[Ванесса] Исправляю смещение заголовков...")
                df.columns = df.iloc[0]
                df = df.drop(df.index[0]).reset_index(drop=True)

        # ЧИСТКА НАЗВАНИЙ
        df.columns = [str(c).strip().lower() for c in df.columns]
        df.columns = [f"col_{i}" if c == 'nan' else c for i, c in enumerate(df.columns)]

        # УМНАЯ КОНВЕРТАЦИЯ ТИПОВ
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notnull().sum() > (len(df) * 0.4):
                df[col] = converted
            else:
                df[col] = df[col].astype(str).replace(['nan', 'NaN', 'None', '?'], np.nan)

        print(f"[Ванесса] Система готова. Вижу колонки: {list(df.columns)}")
        return df

    except Exception as e:
        print(f"[Ванесса] Критическая ошибка загрузки: {e}")
        return None

def _require_file(raw: str = "") -> tuple[str | None, pd.DataFrame | None, str | None]:
    """Возвращает (path, df, error). Берёт из контекста если raw пустой."""
    if raw:
        path = smart_find(raw)
        if not path:
            return None, None, f"Сэр, не нашла файл «{raw}»."
        return path, _load_df(path), None
    if _last_file and _current_df is not None:
        return _last_file, _current_df, None
    if _last_file:
        df = _load_df(_last_file)
        if df is not None:
            return _last_file, df, None
    return None, None, "Сэр, сначала скажите 'найди файл [имя]'."

def _find_column(query: str, columns: list) -> str | None:
    """Ищет колонку по запросу: сначала через синонимы, потом через fuzzy."""
    if not _FUZZY_OK:
        return None

    q = query.strip().lower()

    # Словарь синонимов
    synonyms = {
        "sex":      ["пол", "гендер", "мужчина", "женщина", "gender"],
        "age":      ["возраст", "лет", "стаж", "годы"],
        "pclass":   ["класс", "каюта", "class"],
        "fare":     ["цена", "стоимость", "деньги", "плата"],
        "survived": ["выжил", "спасся", "живой"],
        "embarked": ["порт", "город", "посадка"],
    }

    # 1. Проверяем синонимы
    for real_name, aliases in synonyms.items():
        if any(alias in q for alias in aliases):
            match = _fuzz_process.extractOne(real_name, columns, score_cutoff=60)
            if match:
                return match[0]

    # 2. Нечёткий поиск по колонкам (без id/sn)
    safe_cols = [c for c in columns if "id" not in c.lower()]
    match = _fuzz_process.extractOne(q, safe_cols, scorer=_fuzz.WRatio, score_cutoff=50)
    if match:
        print(f"[Ванесса] Нашла колонку: {match[0]} ({match[1]:.0f}%)")
        return match[0]

    return None


# ═══════════════════════════════════════════════
#  _save_plot — ТЕПЕРЬ ВОЗВРАЩАЕТ Figure, НЕ СОХРАНЯЕТ НА ДИСК
# ═══════════════════════════════════════════════

def _save_plot(fig: Figure) -> Figure:
    """
    Раньше сохраняла PNG на диск.
    Теперь просто возвращает объект Figure — Streamlit отрисует его сам.
    """
    print("[Ванесса] График готов, передаю в интерфейс.")
    return fig


# ═══════════════════════════════════════════════
#  2. ПОИСК ФАЙЛА
# ═══════════════════════════════════════════════

def smart_find(text: str) -> str | None:
    """
    Глобальный поиск CSV. Транслитерация + fuzzy.
    Автоматически загружает DataFrame в контекст.
    """
    spoken = _normalize(text).replace(".csv", "").strip()
    print(f"[Ванесса] Ищу файл: «{spoken}»")
    for folder in SEARCH_DIRS:
        if not os.path.isdir(folder):
            continue
        try:
            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs
                           if not any(ex in d for ex in EXCLUDE_DIRS)]
                for f in files:
                    if not f.lower().endswith(".csv"):
                        continue
                    f_stem = _normalize(f.replace(".csv", ""))
                    if _is_match(spoken, f_stem):
                        full_path = os.path.join(root, f)
                        set_last_file(full_path)
                        return full_path
        except PermissionError:
            continue
    return None

find_file = smart_find


# ═══════════════════════════════════════════════
#  3. ПОКАЗ СТРОК
# ═══════════════════════════════════════════════

def show_rows(path: str, mode: str = "head", n: int = 5) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        label = "Первые" if mode == "head" else "Последние"
        print(f"\n[Ванесса] {label} {n} строк — {os.path.basename(path)}:")
        print("─" * 60)
        print(df.head(n).to_string() if mode == "head" else df.tail(n).to_string())
        print("─" * 60)
        return f"Сэр, вывела {label.lower()} {n} строк на экран."
    except Exception as e:
        return f"Сэр, ошибка вывода: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  4. ПОИСК АНОМАЛИЙ
# ═══════════════════════════════════════════════

def find_anomalies(path: str) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        num = df.select_dtypes(include="number")
        if num.empty:
            return "Сэр, числовых колонок нет."
        z    = np.abs((num - num.mean()) / num.std(ddof=0))
        mask = (z > 3).any(axis=1)
        idx  = df[mask].index.tolist()
        print(f"\n[Ванесса] Аномалии (Z > 3) — {os.path.basename(path)}:")
        print("─" * 60)
        if idx:
            print(f"Строк: {len(idx)}, индексы: {idx}")
            print(df.loc[idx].to_string())
        else:
            print("Аномалий не найдено.")
        print("─" * 60)
        return (f"Сэр, аномалии найдены и выведены. Строк: {len(idx)}."
                if idx else "Сэр, аномалий не обнаружено.")
    except Exception as e:
        return f"Сэр, ошибка поиска аномалий: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  5. КОНВЕРТАЦИЯ В EXCEL
# ═══════════════════════════════════════════════

def to_excel(path: str) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        folder   = os.path.dirname(path)
        basename = os.path.basename(path).replace(".csv", "")
        out      = os.path.join(folder, f"{basename}.xlsx")
        df.to_excel(out, index=False, engine="openpyxl")
        print(f"[Ванесса] Excel: {out}")
        return f"Сэр, файл сконвертирован. Сохранён как {basename}.xlsx."
    except ImportError:
        return "Сэр, установите openpyxl: pip install openpyxl."
    except Exception as e:
        return f"Сэр, ошибка конвертации: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  6. ФИЛЬТРАЦИЯ
# ═══════════════════════════════════════════════

def apply_filter(path: str, condition: str) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            return "Сэр, числовых колонок нет."
        condition = text_to_numeric(condition)
        patterns = [
            (r"больше\s+(\d+\.?\d*)",   ">"),
            (r"меньше\s+(\d+\.?\d*)",   "<"),
            (r"равно\s+(\d+\.?\d*)",    "=="),
            (r"не равно\s+(\d+\.?\d*)", "!="),
            (r">=\s*(\d+\.?\d*)",       ">="),
            (r"<=\s*(\d+\.?\d*)",       "<="),
            (r">\s*(\d+\.?\d*)",        ">"),
            (r"<\s*(\d+\.?\d*)",        "<"),
        ]
        op, val = None, None
        for pattern, operator in patterns:
            m = re.search(pattern, condition)
            if m:
                op  = operator
                val = float(m.group(1))
                break
        if op is None:
            return "Сэр, не распознал условие. Скажите: 'больше 1000' или 'меньше пятьдесят'."
        col  = num_cols[0]
        ops  = {">": df[col] > val, "<": df[col] < val,
                "==": df[col] == val, "!=": df[col] != val,
                ">=": df[col] >= val, "<=": df[col] <= val}
        filtered = df[ops[op]]
        print(f"\n[Ванесса] Фильтр: {col} {op} {val}")
        print("─" * 60)
        print(filtered.to_string())
        print(f"─ Итого: {len(filtered)} из {len(df)} ─")
        return f"Сэр, фильтр применён. Найдено {len(filtered)} строк из {len(df)}."
    except Exception as e:
        return f"Сэр, ошибка фильтрации: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  7. СТАТИСТИКА
# ═══════════════════════════════════════════════

def quick_stats(path: str) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        num        = df.select_dtypes(include="number")
        rows, cols = df.shape
        total_nan  = int(df.isnull().sum().sum())
        print(f"\n[Ванесса] Статистика — {os.path.basename(path)}:")
        print("─" * 60)
        print(f"Строк: {rows} | Колонок: {cols} | Пропусков: {total_nan}")
        if not num.empty:
            for col in num.columns:
                print(f"  {col}: среднее={num[col].mean():.2f}, NaN={int(num[col].isnull().sum())}")
        print("─" * 60)
        if not num.empty:
            means = ", ".join(f"{c}: {num[c].mean():.1f}" for c in num.columns[:3])
            return f"Сэр, {rows} строк, {total_nan} пропусков. Средние: {means}. Детали на экране."
        return f"Сэр, {rows} строк, {total_nan} пропусков. Числовых колонок нет."
    except Exception as e:
        return f"Сэр, ошибка статистики: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  8. АНАЛИЗ (info)
# ═══════════════════════════════════════════════

def analyze_data(path: str) -> str:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        rows, cols = df.shape
        nulls = int(df.isnull().sum().sum())
        dupes = int(df.duplicated().sum())
        print("\n[Ванесса] df.info():")
        df.info()
        return f"Сэр, {rows} строк, {cols} колонок. Пустых: {nulls}. Дубликатов: {dupes}."
    except Exception as e:
        return f"Сэр, ошибка анализа: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  9. ОЧИСТКА
# ═══════════════════════════════════════════════

def clean_data(path: str) -> str:
    # Используем _load_df — он корректно определяет разделитель и кодировку,
    # иначе файл с «;» схлопывается в одну колонку и индексы 0-9 становятся данными
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл."
    try:
        before  = len(df)
        dupes   = int(df.duplicated().sum())
        nans    = int(df.isnull().sum().sum())

        df = df.drop_duplicates()
        # Заполняем пропуски: числа — медианой, текст — «Неизвестно»
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Неизвестно")

        df = df.reset_index(drop=True)   # ← сброс индекса, чтобы не утекал в CSV
        removed = before - len(df)

        folder   = os.path.dirname(path)
        basename = os.path.basename(path)
        out      = os.path.join(folder, f"cleaned_{basename}")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        set_last_file(out)
        print(f"[Ванесса] Очистка: дубликатов={dupes}, пропусков={nans}, удалено строк={removed}")
        return (
            f"Сэр, очистка завершена. "
            f"Дубликатов удалено: {dupes}. "
            f"Пропусков заполнено: {nans}. "
            f"Файл: cleaned_{basename}."
        )
    except PermissionError:
        return "Сэр, нет прав на запись."
    except Exception as e:
        return f"Сэр, ошибка очистки: {type(e).__name__}."


# ═══════════════════════════════════════════════
#  10. УМНАЯ ВИЗУАЛИЗАЦИЯ
#  Возвращает: tuple[str, Figure | None]
#  — текстовый ответ + объект фигуры (или None)
# ═══════════════════════════════════════════════

def smart_plot(path: str, query: str = "") -> tuple[str, Figure | None]:
    df = _load_df(path)
    if df is None:
        return "Сэр, не удалось открыть файл.", None

    # ── ЧЁРНЫЙ СПИСОК: никаких графиков по ID и порядковым номерам ──────
    blacklist = ['sn', 'id', 'unnamed', 'index', 'nan', 'идентификатор']
    all_cols  = [c for c in df.columns if not any(b in c.lower() for b in blacklist)]

    num_cols = [c for c in all_cols if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in all_cols if not pd.api.types.is_numeric_dtype(df[c])]

    q     = query.lower().strip()
    words = [w for w in re.findall(r"[а-яёa-z]+", q) if len(w) >= 3]

    # ── Ищем нужные колонки в запросе через fuzzy + синонимы ────────────
    found_num: list[str] = []
    found_cat: list[str] = []
    for word in words:
        col_n = _find_column(word, num_cols)
        if col_n and col_n not in found_num:
            found_num.append(col_n)
        col_c = _find_column(word, cat_cols)
        if col_c and col_c not in found_cat:
            found_cat.append(col_c)

    # ── БЫСТРЫЕ ТЕКСТОВЫЕ ОТВЕТЫ (без графика) ──────────────────────────
    target_col = found_num[0] if found_num else (found_cat[0] if found_cat else None)
    if target_col:
        data = df[target_col].dropna()
        if any(w in q for w in ["сколько", "количеств"]):
            return f"Сэр, в колонке «{target_col}» я насчитала {len(data)} записей.", None
        if target_col in num_cols:
            if "средн" in q:
                return f"Сэр, среднее в «{target_col}» — {data.mean():.2f}.", None
            if "макс" in q or "больш" in q:
                return f"Сэр, максимум в «{target_col}» — {data.max()}.", None
            if "мин" in q or "меньш" in q:
                return f"Сэр, минимум в «{target_col}» — {data.min()}.", None

    # ── БЛОК ПОСТРОЕНИЯ ГРАФИКОВ ─────────────────────────────────────────
    try:
        force_pie   = any(w in q for w in ["круговая", "круг", "пирог", "pie"])
        force_hist  = any(w in q for w in ["гистограмма", "распределение", "hist"])
        force_box   = any(w in q for w in ["ящик", "боксплот", "boxplot", "box", "квартил"])

        # СЛУЧАЙ BOX: Ящик с усами по числовым колонкам
        if force_box:
            cols_to_plot = found_num if found_num else num_cols[:6]  # максимум 6 колонок
            if not cols_to_plot:
                return "Сэр, числовых колонок нет для боксплота.", None
            fig, ax = plt.subplots(figsize=(max(8, len(cols_to_plot) * 2), 6))
            data_to_plot = [df[c].dropna().values for c in cols_to_plot]
            bp = ax.boxplot(data_to_plot, patch_artist=True, notch=False)
            colors = plt.cm.Paired.colors
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)
            ax.set_xticks(range(1, len(cols_to_plot) + 1))
            ax.set_xticklabels(cols_to_plot, rotation=30, ha="right")
            ax.set_title("Ящик с усами (Box Plot)")
            ax.set_ylabel("Значения")
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            fig.tight_layout()
            return f"Сэр, боксплот по {len(cols_to_plot)} колонкам готов.", _save_plot(fig)

        # СЛУЧАЙ 0: Круговая / одна категория без числовой
        if (force_pie or (len(found_cat) == 1 and not found_num)) and (found_cat or found_num):
            col    = found_cat[0] if found_cat else found_num[0]
            counts = df[col].dropna().value_counts()

            if len(counts) > 10:
                # Слишком много категорий → столбчатая
                fig, ax = plt.subplots(figsize=(10, 5))
                counts.plot(kind="bar", ax=ax, color="steelblue", edgecolor="white")
                ax.set_title(f"Распределение: {col}")
                ax.tick_params(axis="x", rotation=45)
                fig.tight_layout()
                return (
                    f"Сэр, слишком много категорий — сделала столбчатую диаграмму по «{col}».",
                    _save_plot(fig),
                )

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(
                counts.values,
                labels=[str(x) for x in counts.index],
                autopct="%1.1f%%",
                startangle=90,
                colors=plt.cm.Paired.colors,
            )
            ax.set_title(f"Распределение: {col}")
            fig.tight_layout()
            return f"Сэр, круговая диаграмма по «{col}» готова.", _save_plot(fig)

        # СЛУЧАЙ 1: Гистограмма / одна числовая колонка
        if force_hist or (len(found_num) == 1 and not found_cat):
            col = found_num[0] if found_num else None
            if not col:
                return "Сэр, гистограмма требует числовой колонки.", None
            fig, ax = plt.subplots(figsize=(9, 5))
            df[col].dropna().hist(ax=ax, bins=30, color="steelblue", edgecolor="white")
            ax.set_title(f"Гистограмма: {col}")
            ax.set_xlabel(col)
            ax.set_ylabel("Частота")
            fig.tight_layout()
            return f"Сэр, гистограмма по «{col}» готова.", _save_plot(fig)

        # СЛУЧАЙ 2: Категория + Число → Bar Groupby
        if found_cat and found_num:
            c_col, n_col = found_cat[0], found_num[0]
            grouped = df.groupby(c_col)[n_col].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(10, 5))
            grouped.plot(kind="bar", ax=ax, color="steelblue", edgecolor="white")
            ax.set_title(f"Среднее «{n_col}» по «{c_col}»")
            ax.set_xlabel(c_col)
            ax.set_ylabel(f"Среднее {n_col}")
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()
            return (
                f"Сэр, сравнение «{n_col}» по «{c_col}» готово.",
                _save_plot(fig),
            )

        # СЛУЧАЙ 3: Две числовые → Scatter
        if len(found_num) >= 2:
            x, y = found_num[0], found_num[1]
            fig, ax = plt.subplots(figsize=(9, 6))
            ax.scatter(df[x], df[y], alpha=0.5, color="steelblue")
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_title(f"Зависимость «{y}» от «{x}»")
            fig.tight_layout()
            return f"Сэр, точечный график «{x}» и «{y}» готов.", _save_plot(fig)

        # Колонки не найдены — подсказка пользователю
        return (
            "Сэр, не смогла определить колонку для графика. "
            "Скажите точнее, например: 'круговая пол' или 'гистограмма возраст'.",
            None,
        )

    except Exception as e:
        plt.close("all")
        return f"Сэр, ошибка при построении графика: {e}", None

quick_plot = smart_plot


# ═══════════════════════════════════════════════
#  ГЛАВНЫЙ РОУТЕР
#  Всегда возвращает tuple[str, Figure | None]
# ═══════════════════════════════════════════════

def filter_data(text: str) -> tuple[str, Figure | None]:
    """
    Роутер для всех data-команд.
    Всегда возвращает (ответ: str, фигура: Figure | None).
    """
    text = text_to_numeric(text)
    t    = text.lower().strip()

    # ── Выход из файла ───────────────────────────────────────────────────
    if any(w in t for w in ["выход из файла", "закрой файл",
                             "забудь файл", "сбрось файл"]):
        if get_last_file():
            name = os.path.basename(get_last_file())
            set_last_file(None)
            return f"Сэр, файл {name} закрыт. Память очищена.", None
        return "Сэр, нет открытого файла.", None

    # ── Найти файл ───────────────────────────────────────────────────────
    if "найди файл" in t or "открой файл" in t:
        raw  = t.replace("найди файл", "").replace("открой файл", "").strip()
        path = smart_find(raw)
        if path:
            df = _load_df(path)
            msg = f"Сэр, файл найден: {os.path.basename(path)} ({df.shape[0]} строк, {df.shape[1]} колонок)."
            # Возвращаем DataFrame — interface.py покажет его через st.dataframe
            return msg, df
        return f"Сэр, файл «{raw}» не найден.", None

    # ── Показать строки ──────────────────────────────────────────────────
    if any(w in t for w in ["покажи", "выведи", "первые", "последние"]):
        path, df, err = _require_file()
        if err:
            return err, None
        mode = "tail" if "последни" in t else "head"
        m    = re.search(r"(\d+)", t)
        n    = int(m.group(1)) if m else 5
        return show_rows(path, mode, n), None

    # ── Аномалии ─────────────────────────────────────────────────────────
    if any(w in t for w in ["аномали", "найди ошибки", "выбросы"]):
        path, df, err = _require_file()
        if err:
            return err, None
        return find_anomalies(path), None

    # ── В Excel ──────────────────────────────────────────────────────────
    if any(w in t for w in ["в эксель", "вексель", "в excel", "конвертируй"]):
        path, df, err = _require_file()
        if err:
            return err, None
        return to_excel(path), None

    # ── Фильтр ───────────────────────────────────────────────────────────
    if any(w in t for w in ["фильтруй", "фильтр", "отфильтруй"]):
        path, df, err = _require_file()
        if err:
            return err, None
        condition = (
            t.replace("фильтруй", "")
             .replace("фильтр", "")
             .replace("отфильтруй", "")
             .strip()
        )
        if not condition:
            return "Сэр, уточните условие. Например: 'фильтруй больше пятьдесят'.", None
        return apply_filter(path, condition), None

    # ── Статистика ───────────────────────────────────────────────────────
    if any(w in t for w in ["статистика", "средних", "средние", "среднее", "статс"]):
        path, df, err = _require_file()
        if err:
            return err, None
        return quick_stats(path), None

    # ── Графики ──────────────────────────────────────────────────────────
    _PLOT_WORDS = [
        "график", "круговая", "круг", "пирог",
        "гистограмма", "распределение",
        "столбчатая", "сравни", "сравнение",
        "scatter", "точечный",
        "нарисуй", "построй", "покажи диаграмму",
        "ящик", "боксплот", "boxplot", "box", "квартил",
    ]
    if any(w in t for w in _PLOT_WORDS):
        path, df, err = _require_file()
        if err:
            return err, None
        # smart_plot уже возвращает (str, Figure | None) — просто пробрасываем
        return smart_plot(path, t)

    # ── Анализ ───────────────────────────────────────────────────────────
    if any(w in t for w in ["анализ", "проанализируй", "что в файле"]):
        raw = (
            t.replace("анализ файла", "")
             .replace("проанализируй файл", "")
             .replace("что в файле", "")
             .replace("анализ", "")
             .strip()
        )
        path, df, err = _require_file(raw)
        if err:
            return err, None
        return analyze_data(path), None

    # ── Очистка ──────────────────────────────────────────────────────────
    if any(w in t for w in ["очисти", "очистить", "удали дубликаты", "почисти"]):
        raw = (
            t.replace("очисти файл", "")
             .replace("удали дубликаты", "")
             .replace("почисти файл", "")
             .replace("очисти", "")
             .replace("почисти", "")
             .strip()
        )
        path, df, err = _require_file(raw)
        if err:
            return err, None
        return clean_data(path), None

    # Команда не распознана — сигнал роутеру в interface.py идти в нейросеть
    return None, None