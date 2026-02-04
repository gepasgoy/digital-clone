import streamlit as st
import requests

API = "http://localhost:8000"

st.title("📝 Регистрация (3 этапа)")
tab1, tab2 = st.tabs(["Регистрация", "Логин"])

# ---------- РЕГИСТРАЦИЯ ----------
with tab1:
    step = st.radio("Этап", [1, 2, 3], horizontal=True)

    if step == 1:
        email = st.text_input("Email", key="s1_email")
        password = st.text_input("Пароль", type="password", key="s1_pass")

        if st.button("Отправить код"):
            r = requests.post(f"{API}/register/step1",
                json={"email": email, "password": password})
            st.json(r.json())

    if step == 2:
        email = st.text_input("Email", key="s2_email")
        code = st.text_input("Код из email", key="s2_code")

        if st.button("Подтвердить"):
            r = requests.post(f"{API}/register/step2",
                json={"email": email, "code": code})
            st.json(r.json())

    if step == 3:
        email = st.text_input("Email", key="s3_email")
        height = st.number_input("Рост", 100, 250, key="s3_height")
        weight = st.number_input("Вес", 30, 300, key="s3_weight")

        if st.button("Завершить регистрацию"):
            r = requests.post(f"{API}/register/step3",
                json={"email": email, "height": height, "weight": weight})
            st.json(r.json())


# ---------- ЛОГИН ----------
with tab2:
    st.subheader("Вход")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Пароль", type="password", key="login_pass")

    if st.button("Войти"):
        r = requests.post(f"{API}/login",
            json={"email": email, "password": password})
        res = r.json()
        if res["success"]:
            st.success(res["message"])
            st.balloons()
        else:
            st.error(res["message"])


st.sidebar.code("""
uvicorn simple_api:app --reload
streamlit run simple_app.py
""")
