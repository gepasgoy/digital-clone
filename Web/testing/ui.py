import streamlit as st
from api_client import api_get, logout_local
#Не знаю, насколько этот файл целесообразен

def topbar():
    user = st.session_state.get("user", {})
    name = user.get("name", "Пользователь")

    c1, c2, c3 = st.columns([1, 3, 2])

    with c1:
        st.image("../img.png")

    with c2:
        st.subheader(f"👤 {name}")

    with c3:
        b1, b2 = st.columns(2)

        # 🔔 Уведомления
        with b1:
            if st.button("🔔 Уведомления", use_container_width=True):
                st.switch_page("pages/10_Notifications.py")

        # 🚪 Выход
        with b2:
            if st.button("Выйти", use_container_width=True):
                logout_local()
                st.switch_page("pages/1_Login.py")

    st.divider()
