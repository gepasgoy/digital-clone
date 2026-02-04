import streamlit as st
from auth import check_auth

check_auth()

st.title("🏠 Главная")
st.write("Вы вошли как:", st.session_state.user)

if st.button("Профиль"):
    st.switch_page("pages/2.py")
