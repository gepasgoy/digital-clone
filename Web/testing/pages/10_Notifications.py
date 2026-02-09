import streamlit as st
import pandas as pd
from datetime import datetime

from auth import guard
from ui import topbar

guard()
topbar()

st.title("Центр уведомлений")

# 💾 MOCK ДАННЫЕ Тут я мог бы заменить на ручку уведомлений в апи, но оставил чисто для визуального представления, т.к моя ручка тоже чисто номинальная

if "notes" not in st.session_state:
    st.session_state.notes = [
        {"msg": "Высокий пульс", "type": "critical", "date": datetime.now(), "read": False},
        {"msg": "Давно нет измерений", "type": "warning", "date": datetime.now(), "read": False},
        {"msg": "Новая запись врача", "type": "info", "date": datetime.now(), "read": True},
        {"msg": "Рекомендуется прогулка", "type": "recommend", "date": datetime.now(), "read": False},
    ]

notes = st.session_state.notes

# 🔢 СЧЁТЧИК НЕПРОЧИТАННЫХ

unread = sum(not n["read"] for n in notes)
st.metric("Непрочитанных", unread)

if st.button("Отметить всё прочитанным"):
    for n in notes:
        n["read"] = True
    st.rerun()

# ⚙️ НАСТРОЙКИ ОПОВЕЩЕНИЙ

st.subheader("Настройки")

if "notify_settings" not in st.session_state:
    st.session_state.notify_settings = {
        "email": True,
        "push": True
    }

s = st.session_state.notify_settings

s["email"] = st.toggle("Email уведомления", s["email"])
s["push"] = st.toggle("Push уведомления", s["push"])

# 📚 ГРУППИРОВКА

st.subheader("Уведомления")

df = pd.DataFrame(notes)
df["date"] = pd.to_datetime(df["date"])
df["day"] = df["date"].dt.date

group_mode = st.radio(
    "Группировать",
    ["По типу", "По дате"],
    horizontal=True
)

# 🎨 ЦВЕТА

def show_note(row):
    text = ("🔵 " if not row.read else "⚪ ") + row.msg

    if row.type == "critical":
        st.error(text)
    elif row.type == "warning":
        st.warning(text)
    elif row.type == "info":
        st.info(text)
    else:
        st.success(text)

# 🗂 ВЫВОД

if group_mode == "По типу":

    for t in ["critical", "warning", "info", "recommend"]:
        block = df[df["type"] == t]
        if block.empty:
            continue

        st.markdown(f"### {t.upper()}")

        for i, row in block.iterrows():
            show_note(row)

            if not row.read:
                if st.button("Прочитано", key=f"r{i}"):
                    st.session_state.notes[i]["read"] = True
                    st.rerun()

else:

    for day, block in df.groupby("day"):
        st.markdown(f"### {day}")

        for i, row in block.iterrows():
            show_note(row)

            if not row.read:
                if st.button("Прочитано", key=f"d{i}"):
                    st.session_state.notes[i]["read"] = True
                    st.rerun()
