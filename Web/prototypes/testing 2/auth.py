import streamlit as st

def set_auth(email, response_data):
    st.session_state["authenticated"] = True
    st.session_state["user"] = email
    st.session_state["access_token"] = response_data.get("access_token")
    st.session_state["cookies"] = {"my_token": response_data.get("access_token", "")}

def check_auth():
    if not st.session_state.get("authenticated", False):
        st.error("Пожалуйста, войдите в систему")
        st.switch_page("simple_app.py")
        st.stop()

def clear_auth():
    for key in ["authenticated", "user", "access_token", "refresh_token", "cookies"]:
        st.session_state.pop(key, None)