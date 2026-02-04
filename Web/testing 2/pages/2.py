import streamlit as st
from auth import check_auth
from api_client import logout

check_auth()

st.title("👤 Профиль")

st.write(f"### Информация о пользователе")
st.write(f"**Email:** {st.session_state.user}")
st.write(f"**Статус:** Аутентифицирован")

st.divider()

st.write("### Действия")

if st.button("🚪 Выход из системы"):
    logout_result = logout()
    from auth import clear_auth
    clear_auth()
    st.success("Выход выполнен успешно")
    st.rerun()

if st.button("🏠 На главную"):
    st.switch_page("pages/1.py")

st.divider()
st.write("### Техническая информация")
if st.button("Показать/скрыть токены", type="secondary"):
    if "show_tokens" not in st.session_state:
        st.session_state.show_tokens = False
    st.session_state.show_tokens = not st.session_state.show_tokens

if st.session_state.get("show_tokens", False):
    st.code(f"Access Token: {st.session_state.get('access_token', 'Нет')[:50]}...")
    st.code(f"Refresh Token: {st.session_state.get('refresh_token', 'Нет')[:50]}...")