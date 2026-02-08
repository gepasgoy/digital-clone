import streamlit as st
from api_client import login, register_user
from auth import set_auth

st.title("🔐 Вход / Регистрация")

tab1, tab2 = st.tabs(["Логин", "Регистрация"])

with tab1:
    email = st.text_input("Email", key="l_email")
    password = st.text_input("Пароль", type="password", key="l_pass")

    if st.button("Войти"):
        if not email or not password:
            st.error("Заполните все поля")
        else:
            r = login(email, password)
            if "access_token" in r:  # Успешный вход
                set_auth(email, r)
                st.success("Вход выполнен успешно!")
                st.rerun()  # Обновляем страницу
            else:
                st.error(r.get("message", "Ошибка входа"))

with tab2:
    st.write("### Регистрация нового пользователя")
    
    email = st.text_input("Email", key="r_email")
    password = st.text_input("Пароль", type="password", key="r_pass")
    name = st.text_input("Имя", key="r_name")
    
    if st.button("Зарегистрироваться"):
        if not email or not password or not name:
            st.error("Заполните все поля")
        else:
            r = register_user(email, password, name)
            if r.get("success"):
                st.success(r["message"])
                # Автоматический вход после регистрации
                login_r = login(email, password)
                if "access_token" in login_r:
                    set_auth(email, login_r)
                    st.success("Автоматический вход выполнен!")
                    st.rerun()
            else:
                st.error(r["message"])

# Если пользователь аутентифицирован, показываем главную страницу
if st.session_state.get("authenticated", False):
    st.switch_page("pages/1.py")