import streamlit as st
from api_client import api_get, logout_local


def topbar():
    user = st.session_state.get("user", {})
    name = user.get("name", "Пользователь")

    c1, c2, c3, c4 = st.columns([2, 4, 2, 1])

    with c1:
        st.markdown("## 🏥 MedApp")

    with c2:
        st.write(f"👤 {name}")

    with c3:
        if st.button("🔔"):
            r = api_get("/notifications")
            if r.ok:
                st.write(r.json())
            else:
                st.warning("Нет уведомлений")

    with c4:
        if st.button("🚪"):
            logout_local()
            st.switch_page("pages/1_Login.py")


def sidebar_menu():
    with st.sidebar:
        st.title("Меню")

        st.page_link("pages/2_Dashboard.py", label="Главная")
        st.page_link("pages/3_Indicators.py", label="Мои показатели")
        st.page_link("pages/4_Treatment.py", label="Назначения")
        st.page_link("pages/5_Diary.py", label="Дневник")
        st.page_link("pages/6_Stats.py", label="Статистика")
        st.page_link("pages/7_Visits.py", label="Визиты")
        st.page_link("pages/8_Settings.py", label="Настройки")
        st.page_link("pages/9_Help.py", label="Помощь")
