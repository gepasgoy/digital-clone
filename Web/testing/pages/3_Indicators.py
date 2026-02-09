import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from auth import guard
from api_client import api_get, api_post
from ui import topbar

guard()
topbar()

st.title("Мои показатели — Пульс")

user = st.session_state.user
pid = user.get("patient_id")

if not pid:
    st.warning("Пациент не привязан")
    st.stop()

# =====================================================
# ✅ ФОРМА ВВОДА
# =====================================================

st.subheader("Добавить измерение")

pulse = st.number_input("Пульс", 30, 220)

if st.button("Сохранить измерение", use_container_width=True):

    if pulse < 40 or pulse > 200:
        st.error("Допустимый диапазон 40–200")
        st.stop()

    r = api_post("/pulse-monitoring", {
        "value": pulse,
        "patient_id": pid
    })

    if r.ok:
        st.success("Сохранено")
        st.rerun()
    else:
        st.error(r.text)

# =====================================================
# 📥 ЗАГРУЗКА ДАННЫХ
# =====================================================

r = api_get(f"/medical-card?patient_id={pid}")

if not r.ok:
    st.error("Нет данных")
    st.stop()

data = r.json()["pulse_monitoring"]

if not data:
    st.info("Нет измерений")
    st.stop()

df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df["date"])

# =====================================================
# 📊 ГРАФИК С ПЕРИОДОМ
# =====================================================

st.subheader("Динамика")

period = st.selectbox(
    "Период",
    ["7 дней", "30 дней", "90 дней", "Все"]
)

days_map = {
    "7 дней": 7,
    "30 дней": 30,
    "90 дней": 90
}

if period != "Все":
    cutoff = datetime.now() - timedelta(days=days_map[period])
    df_plot = df[df["date"] >= cutoff]
else:
    df_plot = df

st.line_chart(
    df_plot.set_index("date")["value"]
)

# =====================================================
# 📋 ТАБЛИЦА + ФИЛЬТРЫ
# =====================================================

st.subheader("История измерений")

c1, c2 = st.columns(2)

with c1:
    min_val = st.number_input("Мин пульс", 0, 300, 0)

with c2:
    max_val = st.number_input("Макс пульс", 0, 300, 300)

df_table = df[
    (df["value"] >= min_val) &
    (df["value"] <= max_val)
].sort_values("date", ascending=False)

st.dataframe(
    df_table[["date", "value"]],
    use_container_width=True
)
