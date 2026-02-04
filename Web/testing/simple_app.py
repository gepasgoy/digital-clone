import streamlit as st
from api_client import login, reg1, reg2, reg3
from auth import set_auth

st.title("🔐 Вход / Регистрация")

tab1, tab2 = st.tabs(["Логин", "Регистрация"])

with tab1:
    email = st.text_input("Email", key="l_email")
    password = st.text_input("Пароль", type="password", key="l_pass")

    if st.button("Войти"):
        r = login(email, password)
        if r["success"]:
            set_auth(email)
            st.switch_page("pages/1_🏠_Главная.py")
        else:
            st.error(r["message"])


with tab2:
    step = st.radio("Шаг", [1,2,3], horizontal=True)

    if step == 1:
        if st.button("Шаг 1 — отправить код"):
            st.json(reg1(
                st.session_state.get("r_email"),
                st.session_state.get("r_pass")
            ))

        st.text_input("Email", key="r_email")
        st.text_input("Пароль", type="password", key="r_pass")

    if step == 2:
        st.text_input("Email", key="r2_email")
        st.text_input("Код", key="r_code")
        if st.button("Шаг 2"):
            st.json(reg2(
                st.session_state.r2_email,
                st.session_state.r_code
            ))

    if step == 3:
        st.text_input("Email", key="r3_email")
        h = st.number_input("Рост", 100, 250)
        w = st.number_input("Вес", 30, 300)

        if st.button("Шаг 3"):
            st.json(reg3(
                st.session_state.r3_email, h, w
            ))
