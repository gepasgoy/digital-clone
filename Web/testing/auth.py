import streamlit as st

def set_auth(email):
    st.session_state.auth = True
    st.session_state.user = email

def check_auth():
    if not st.session_state.get("auth"):
        st.warning("Нужно войти")
        st.stop()
