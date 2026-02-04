import streamlit as st

def set_auth(email, response_data):
    """Установка данных аутентификации в сессию"""
    st.session_state["authenticated"] = True
    st.session_state["user"] = email
    st.session_state["access_token"] = response_data.get("access_token")
    st.session_state["refresh_token"] = response_data.get("refresh_token")
    
    # Сохраняем cookies для дальнейшего использования
    # В реальном приложении нужно сохранять cookies из response
    st.session_state["cookies"] = {
        "my_token": response_data.get("access_token", "")
    }

def check_auth():
    """Проверка аутентификации пользователя"""
    if not st.session_state.get("authenticated", False):
        st.error("Пожалуйста, войдите в систему")
        st.switch_page("simple_app.py")
        st.stop()

def clear_auth():
    """Очистка данных аутентификации"""
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user" in st.session_state:
        del st.session_state["user"]
    if "access_token" in st.session_state:
        del st.session_state["access_token"]
    if "refresh_token" in st.session_state:
        del st.session_state["refresh_token"]
    if "cookies" in st.session_state:
        del st.session_state["cookies"]