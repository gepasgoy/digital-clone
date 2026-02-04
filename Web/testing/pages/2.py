import streamlit as st
from auth import check_auth

check_auth()

st.title("👤 Профиль")
st.write("Пользователь:", st.session_state.user)

if st.button("Выход"):
    st.session_state.clear()
    st.switch_page("simple_app.py")
