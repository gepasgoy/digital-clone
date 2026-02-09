import streamlit as st
import pandas as pd
from datetime import datetime

from auth import guard
from ui import topbar

guard()
topbar()

st.title("Дневник самочувствия")

# =====================================================
# 💾 ХРАНИЛИЩЕ (пока локально)
# =====================================================

if "diary" not in st.session_state:
    st.session_state.diary = []

# =====================================================
# 😊 БЫСТРАЯ ЗАПИСЬ — EMOJI ШКАЛА
# =====================================================

st.subheader("Быстрая запись")

mood = st.radio(
    "Как самочувствие?",
    ["😄 Отлично", "🙂 Нормально", "😐 Так себе", "😞 Плохо", "🤒 Очень плохо"],
    horizontal=True
)

if st.button("Записать быстро", use_container_width=True):
    st.session_state.diary.append({
        "date": datetime.now(),
        "type": "quick",
        "mood": mood,
        "symptoms": [],
        "intensity": None,
        "text": ""
    })
    st.success("Записано")

# =====================================================
# 📝 ДЕТАЛЬНАЯ ЗАПИСЬ
# =====================================================

st.subheader("Детальная запись")

symptoms = st.multiselect(
    "Симптомы",
    [
        "Головная боль",
        "Слабость",
        "Одышка",
        "Боль в груди",
        "Головокружение",
        "Тошнота",
    ]
)

intensity = st.slider("Интенсивность", 1, 10, 5)

comment = st.text_area("Комментарий")

if st.button("Сохранить запись", use_container_width=True):
    st.session_state.diary.append({
        "date": datetime.now(),
        "type": "full",
        "mood": None,
        "symptoms": symptoms,
        "intensity": intensity,
        "text": comment
    })
    st.success("Сохранено")

# =====================================================
# 📚 АРХИВ + ФИЛЬТРЫ
# =====================================================

st.subheader("Архив записей")

data = st.session_state.diary

if not data:
    st.info("Записей пока нет")
    st.stop()

df = pd.DataFrame(data)

# --- фильтр по дате

c1, c2 = st.columns(2)

with c1:
    d_from = st.date_input("С даты")

with c2:
    d_to = st.date_input("По дату")

df["date"] = pd.to_datetime(df["date"])

mask = (
    (df["date"].dt.date >= d_from) &
    (df["date"].dt.date <= d_to)
)

df = df[mask]

# --- фильтр по симптомам

sym_filter = st.multiselect(
    "Фильтр по симптомам",
    sorted({s for row in df["symptoms"] for s in row})
)

if sym_filter:
    df = df[df["symptoms"].apply(
        lambda lst: any(s in lst for s in sym_filter)
    )]

# =====================================================
# 📋 ВЫВОД
# =====================================================

for _, row in df.sort_values("date", ascending=False).iterrows():

    with st.container():
        st.markdown(f"**{row['date'].strftime('%d.%m %H:%M')}**")

        if row["mood"]:
            st.write("Самочувствие:", row["mood"])

        if row["symptoms"]:
            st.write("Симптомы:", ", ".join(row["symptoms"]))

        if row["intensity"]:
            st.progress(row["intensity"] / 10)

        if row["text"]:
            st.caption(row["text"])

        st.divider()
