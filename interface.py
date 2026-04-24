import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ──────────────────────────────────────────────
# 1. ЛЕНИВЫЕ ИМПОРТЫ
# ──────────────────────────────────────────────

def get_brain():
    import brain
    return brain

def get_stt():
    import stt
    return stt

def get_tts():
    import tts
    return tts

# ──────────────────────────────────────────────
# 2. НАСТРОЙКИ СТРАНИЦЫ
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Vanessa AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Общий фон ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    color: #e0e0e0;
}
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stAppViewContainer"] > .main > div { padding-top: 1.5rem; }

/* ── Заголовки секций ── */
.section-title {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #7b8cde;
    margin-bottom: 0.6rem;
}

/* ── Пузыри сообщений ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* Весь текст внутри чата — чисто белый, без переливов */
[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #e8eaf0 !important;
    -webkit-text-fill-color: #e8eaf0 !important;
    background: transparent !important;
    background-clip: unset !important;
    -webkit-background-clip: unset !important;
}

/* ── Поле ввода ── */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: rgba(30, 30, 60, 0.85) !important;
    border: 1px solid rgba(123,140,222,0.4) !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
    -webkit-text-fill-color: #e8eaf0 !important;
    caret-color: #a78bfa !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #7b8cde !important;
    box-shadow: 0 0 0 2px rgba(123,140,222,0.25) !important;
}
/* Плейсхолдер */
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(160,174,192,0.5) !important;
    -webkit-text-fill-color: rgba(160,174,192,0.5) !important;
}
/* Обёртка поля */
[data-testid="stChatInput"] {
    background: transparent !important;
}

/* ── Кнопки ── */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 2.8em;
    font-weight: 600;
    letter-spacing: 0.04em;
    transition: all 0.2s;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7b8cde, #a78bfa) !important;
    border: none !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(123,140,222,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #ccc !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #a0aec0 !important;
}

/* ── Инфо-блок ── */
[data-testid="stAlert"] {
    background: rgba(123,140,222,0.1) !important;
    border: 1px solid rgba(123,140,222,0.3) !important;
    border-radius: 12px !important;
    color: #a0b4ff !important;
}

/* ── Метрика ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 0.6rem 1rem;
}
[data-testid="stMetricLabel"] { color: #7b8cde !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #e0e0e0 !important; }

/* ── Пилюля статуса ── */
.metric-pill {
    display: inline-block;
    background: rgba(123,140,222,0.15);
    border: 1px solid rgba(123,140,222,0.3);
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.75rem;
    color: #a0b4ff;
    margin: 0.15rem;
}

/* ── Логотип ── */
.vanessa-logo {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7b8cde, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.vanessa-sub {
    font-size: 0.72rem;
    color: #556;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── Разделитель ── */
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 3. КОНСТАНТЫ
# ──────────────────────────────────────────────

PC_TRIGGERS = [
    "открой", "запусти", "включи", "запускай",
    "закрой", "убей", "вырубай", "вырубить",
    "найди в интернете",
    "громче", "тише", "выключи звук", "включи звук",
    "без звука", "верни звук",
]

DATA_TRIGGERS = [
    "файл", "найди файл", "открой файл", "закрой файл",
    "забудь файл", "сбрось файл",
    "первые", "последние",
    "анализ", "проанализируй", "что в файле",
    "статистика", "среднее", "средние", "средних", "статс",
    "фильтруй", "фильтр", "отфильтруй",
    "очисти", "очистить", "почисти", "удали дубликаты",
    "аномали", "выбросы", "найди ошибки",
    "конвертируй", "в эксель", "в excel", "вексель",
    "график", "гистограмма", "распределение",
    "круговая", "круг", "пирог",
    "столбчатая", "сравни", "сравнение",
    "scatter", "точечный", "нарисуй", "построй",
    "ящик", "боксплот", "boxplot", "box", "квартил",
]

EXIT_WORDS = {"стоп", "выход", "пока", "хватит", "отбой", "выключи"}


# ──────────────────────────────────────────────
# 4. ОБРАБОТКА КОМАНДЫ
# ──────────────────────────────────────────────

def process_command(text: str) -> tuple[str, Figure | pd.DataFrame | None]:
    if not text or not text.strip():
        return "Команда не распознана.", None

    lower = text.lower().strip()

    if any(t in lower for t in PC_TRIGGERS):
        import skills_pc
        return skills_pc.filter_pc(lower), None

    if any(t in lower for t in DATA_TRIGGERS):
        import skills_data
        result = skills_data.filter_data(lower)
        if isinstance(result, tuple):
            reply, visual = result
            if reply is not None:
                return reply, visual

    return get_brain().get_answer(lower), None


# ──────────────────────────────────────────────
# 5. SESSION STATE
# ──────────────────────────────────────────────

for _k, _v in {
    "messages":           [],
    "dashboard_elements": [],
    "voice_active":       False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ──────────────────────────────────────────────
# 6. САЙДБАР
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="vanessa-logo">✦ Vanessa</div>', unsafe_allow_html=True)
    st.markdown('<div class="vanessa-sub">AI Data Assistant</div>', unsafe_allow_html=True)

    # Статус текущего файла
    try:
        import skills_data as _sd, os as _os
        cur = _sd.get_last_file()
        if cur:
            df_cur = _sd.get_current_df()
            shape  = f"{df_cur.shape[0]}×{df_cur.shape[1]}" if df_cur is not None else "—"
            st.markdown(
                f'<span class="metric-pill">📂 {_os.path.basename(cur)}</span>'
                f'<span class="metric-pill">🔢 {shape}</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="metric-pill">📂 Файл не открыт</span>', unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("---")

    # Голосовой режим
    st.markdown('<div class="section-title">🎙 Голосовой режим</div>', unsafe_allow_html=True)
    if not st.session_state.voice_active:
        if st.button("Запустить", type="primary"):
            st.session_state.voice_active = True
            st.rerun()
        st.caption("Скажите **«Ванесса»** + команда. **«Стоп»** — выход.")
    else:
        st.markdown("🔴 **Слушаю…**")
        if st.button("Остановить", type="secondary"):
            st.session_state.voice_active = False
            st.rerun()

    st.markdown("---")

    # Шпаргалка
    st.markdown('<div class="section-title">💡 Команды</div>', unsafe_allow_html=True)

    cmd_data, cmd_pc = st.tabs(["📊 Данные", "💻 ПК"])

    with cmd_data:
        st.caption(
            "📂 `найди файл titanic`\n\n"
            "🥧 `круговая пол`\n\n"
            "📊 `гистограмма возраст`\n\n"
            "📦 `ящик возраст`\n\n"
            "📈 `сравни пол и возраст`\n\n"
            "🔍 `фильтруй больше 30`\n\n"
            "🧹 `очисти файл`\n\n"
            "📋 `статистика`\n\n"
            "🔎 `аномалии`\n\n"
            "💾 `конвертируй в excel`"
        )

    with cmd_pc:
        st.caption(
            "**▶ Открыть:**\n\n"
            "`открой браузер`\n\n"
            "`открой дискорд`\n\n"
            "`открой телеграм`\n\n"
            "`открой спотифай`\n\n"
            "`открой стим`\n\n"
            "`открой ютуб`\n\n"
            "`открой блокнот`\n\n"
            "`открой калькулятор`\n\n"
            "**⏹ Закрыть:**\n\n"
            "`закрой хром`\n\n"
            "`закрой дискорд`\n\n"
            "`закрой телеграм`\n\n"
            "**🔊 Звук:**\n\n"
            "`громче` / `тише`\n\n"
            "`выключи звук`\n\n"
            "`включи звук`\n\n"
            "**🌐 Поиск:**\n\n"
            "`найди в интернете кот`"
        )

    st.markdown("---")
    if st.button("🗑 Очистить историю", type="secondary"):
        st.session_state.messages           = []
        st.session_state.dashboard_elements = []
        st.rerun()


# ──────────────────────────────────────────────
# 7. ОСНОВНОЙ КОНТЕНТ
# ──────────────────────────────────────────────

col_chat, col_viz = st.columns([0.42, 0.58], gap="large")

# ── ЧАТ ─────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown('<div class="section-title">🗨 Оперативный чат</div>', unsafe_allow_html=True)

    chat_box = st.container(height=530)
    for msg in st.session_state.messages:
        chat_box.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Введите команду для Ванессы…"):
        if prompt.strip():
            reply, visual = process_command(prompt)
            st.session_state.messages.append({"role": "user",      "content": prompt})
            st.session_state.messages.append({"role": "assistant",  "content": reply})
            if visual is not None:
                st.session_state.dashboard_elements.append(
                    {"label": prompt[:45], "data": visual}
                )
            st.rerun()


# ── ДАШБОРД ──────────────────────────────────────────────────────────────
with col_viz:
    st.markdown('<div class="section-title">📊 Результаты анализа</div>', unsafe_allow_html=True)

    elements = st.session_state.dashboard_elements

    if not elements:
        st.info("Здесь появятся графики и таблицы после ваших команд.")
    else:
        # Разделяем на два потока: графики и таблицы
        charts = []
        tables = []
        for item in elements:
            el = item["data"] if isinstance(item, dict) else item
            lb = item.get("label", "—") if isinstance(item, dict) else "—"
            if isinstance(el, Figure):
                charts.append((lb, el))
            elif isinstance(el, pd.DataFrame):
                tables.append((lb, el))

        tab_charts, tab_tables = st.tabs([
            f"📈 Графики ({len(charts)})",
            f"📋 Таблицы ({len(tables)})",
        ])

        # ── Вкладка: Графики ─────────────────────────────────────────────
        with tab_charts:
            if not charts:
                st.info("Графиков пока нет. Попробуйте: «гистограмма возраст»")
            else:
                for i, (label, fig) in enumerate(reversed(charts)):
                    idx = len(charts) - i
                    prefix = "🆕 " if i == 0 else ""
                    with st.expander(f"{prefix}График #{idx} — {label}", expanded=(i == 0)):
                        # Тёмная тема для matplotlib
                        fig.patch.set_facecolor("#1a1a2e")
                        for ax in fig.axes:
                            ax.set_facecolor("#16213e")
                            ax.tick_params(colors="#a0aec0")
                            ax.xaxis.label.set_color("#a0aec0")
                            ax.yaxis.label.set_color("#a0aec0")
                            ax.title.set_color("#e0e0e0")
                            for spine in ax.spines.values():
                                spine.set_edgecolor("#2d3748")
                        st.pyplot(fig, use_container_width=True)

        # ── Вкладка: Таблицы ─────────────────────────────────────────────
        with tab_tables:
            if not tables:
                st.info("Таблиц пока нет. Попробуйте: «найди файл titanic»")
            else:
                for i, (label, df_el) in enumerate(reversed(tables)):
                    idx = len(tables) - i
                    prefix = "🆕 " if i == 0 else ""
                    with st.expander(f"{prefix}Таблица #{idx} — {label}", expanded=(i == 0)):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Строк",     df_el.shape[0])
                        c2.metric("Колонок",   df_el.shape[1])
                        c3.metric("Пропусков", int(df_el.isnull().sum().sum()))
                        st.dataframe(df_el, use_container_width=True, height=280)


# ──────────────────────────────────────────────
# 8. ГОЛОСОВОЙ ЦИКЛ
# ──────────────────────────────────────────────

if st.session_state.voice_active:
    with st.spinner("🎙️ Слушаю…"):
        command = get_stt().listen()

    if command and command.strip():
        lower = command.lower().strip()

        if set(lower.split()) & EXIT_WORDS:
            st.session_state.messages.append({"role": "user",      "content": command})
            st.session_state.messages.append({"role": "assistant",  "content": "Голосовой режим деактивирован."})
            st.session_state.voice_active = False
            get_tts().va_speak("Голосовой режим деактивирован.")
            st.rerun()
        else:
            reply, visual = process_command(command)
            get_tts().va_speak(reply)
            st.session_state.messages.append({"role": "user",      "content": command})
            st.session_state.messages.append({"role": "assistant",  "content": reply})
            if visual is not None:
                st.session_state.dashboard_elements.append(
                    {"label": command[:45], "data": visual}
                )
            st.rerun()