import streamlit as st
from auth import guard
from api_client import api_get
from ui import topbar

guard()
topbar()

st.title("Главная")

user = st.session_state.user

st.subheader(f"Здравствуйте, {user['name']} 👋")

# =========================
# СВОДКА ЗА СЕГОДНЯ
# =========================

pid = user.get("patient_id")

if pid:
    r = api_get(f"/medical-card?patient_id={pid}")
    if r.ok:
        data = r.json()
        pulse = data["pulse_monitoring"][:1]

        if pulse:
            st.metric("Последний пульс", pulse[0]["value"])
        else:
            st.metric("Последний пульс", "нет данных")

# =========================
# БЫСТРЫЕ ДЕЙСТВИЯ
# =========================

st.divider()
st.subheader("Быстрые действия", text_alignment="center")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("➕ Добавить пульс", use_container_width=1):
        st.switch_page("pages/3_Indicators.py")

with c2:
    if st.button("📝 Жалоба", use_container_width=1):
        st.switch_page("pages/5_Diary.py")

with c3:
    if st.button("📊 Статистика", use_container_width=1):
        st.switch_page("pages/6_Stats.py")
