import streamlit as st
import re
import random
import time
from auth import login_user, register_user

st.session_state.setdefault("login_attempts", 0)
st.session_state.setdefault("lock_until", 0)
st.session_state.setdefault("captcha_ok", False)

def gen_captcha():
    seq = [
        "💧 Запить водой",
        "💊 Принять таблетку",
        "🍽 Поесть"
    ]
    random.shuffle(seq)
    st.session_state.captcha_order = seq
    st.session_state.captcha_ok = False


if "captcha_order" not in st.session_state:
    gen_captcha()



st.title("Авторизация")

mode = st.radio("Режим", ["Вход", "Регистрация"], horizontal=True)

# LOGIN

if mode == "Вход":
    mail = st.text_input("Email")
    password = st.text_input("Пароль", type="password")

    st.subheader("Проверка")

    user_seq = st.multiselect(
        "Выбери правильный порядок приёма лекарства:",
        st.session_state.captcha_order
    )

    if st.button("Проверить порядок"):
        if user_seq == ["🍽 Поесть", "💊 Принять таблетку", "💧 Запить водой"]:
            st.session_state.captcha_ok = True
            st.success("Верно")
        else:
            st.error("Неверный порядок")

    
    if st.button("Войти"):
        now = time.time()

        if now < st.session_state.lock_until:
            st.error("Слишком много попыток. Подожди минуту.")
            st.stop()

        if st.session_state.login_attempts >= 2:
            st.session_state.lock_until = time.time() + 60
            st.error("Блокировка на 1 минуту")
            st.stop()

        if not st.session_state.get("captcha_ok"):
            st.error("Пройди проверку")
            st.session_state.login_attempts = st.session_state.get("login_attempts", 0) + 1
            st.stop()

        ok, err = login_user(mail, password)
        if ok:
            gen_captcha()
            st.session_state.login_attempts = 0
            st.switch_page("pages/2_Dashboard.py")
        else:
            st.session_state.login_attempts = st.session_state.get("login_attempts", 0) + 1
            st.error(err)

# REGISTER — 3 STEP

if mode == "Регистрация":

    if "reg_step" not in st.session_state:
        st.session_state.reg_step = 1
        st.session_state.reg_data = {}

    step = st.session_state.reg_step

    # ---------------- STEP 1 ----------------

    if step == 1:
        st.subheader("Шаг 1 — Базовые данные")

        name = st.text_input("Имя")
        mail = st.text_input("Email")
        password = st.text_input("Пароль", type="password")

        def valid_password(p):
            return (
                len(p) >= 12
                and re.search(r"\d", p)
                and re.search(r"[!@#$%^&*(),.?\":{}|<>]", p)
            )

        if st.button("Далее"):

            if not valid_password(password):
                st.error("Пароль ≥12 символов, цифра и спецсимвол")
                st.stop()

            st.session_state.reg_data = {
                "Name": name,
                "mail": mail,
                "password": password
            }

            code = str(random.randint(100000, 999999))
            st.session_state.email_code = code

            st.session_state.reg_step = 2
            st.rerun()

    # ---------------- STEP 2 ----------------

    elif step == 2:
        st.subheader("Шаг 2 — Подтверждение email")
        st.info(f"📧 Эмуляция email — код: {st.session_state.email_code}")

        code = st.text_input("Введите код из email")

        if st.button("Подтвердить"):
            if code == st.session_state.email_code:
                st.session_state.reg_step = 3
                st.rerun()
            else:
                st.error("Неверный код")

    # ---------------- STEP 3 ----------------

    elif step == 3:
        st.subheader("Шаг 3 — Медицинская анкета")

        height = st.number_input("Рост (см)", 50, 300)
        weight = st.number_input("Вес (кг)", 10, 400)

        if st.button("Завершить регистрацию"):

            if not (100 <= height <= 250):
                st.error("Рост должен быть 100–250 см")
                st.stop()

            if not (30 <= weight <= 300):
                st.error("Вес должен быть 30–300 кг")
                st.stop()

            # сохраняем (если потом добавишь API — отправишь туда)
            st.session_state.reg_data["height"] = height
            st.session_state.reg_data["weight"] = weight

            ok, err = register_user(
                st.session_state.reg_data["mail"],
                st.session_state.reg_data["password"],
                st.session_state.reg_data["Name"],
            )

            if ok:
                st.success("Регистрация завершена")
                st.session_state.reg_step = 1
                st.session_state.reg_data = {}
            else:
                st.error(err)
