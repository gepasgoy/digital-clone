import streamlit as st
from auth import check_auth
check_auth()

st.title("👤 Профиль")
st.write(f"**Email:** {st.session_state.user}")
st.write(f"**Статус:** Аутентифицирован")

if st.button("🚪 Выход из системы"):
    from api_client import logout
    from auth import clear_auth
    logout()
    clear_auth()
    st.success("Выход выполнен успешно")
    st.rerun()

if st.button("🏠 На главную"):
    st.switch_page("pages/1.py")