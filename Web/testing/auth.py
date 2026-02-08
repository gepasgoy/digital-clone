import streamlit as st
from api_client import api_post, api_get

def login_user(mail, password):
    r = api_post("/login", {"mail": mail,"password": password})

    if not r.ok:
        return False, r.text

    d = r.json()

    st.session_state.token = d["access_token"]
    st.session_state.refresh_token = d["refresh_token"]
    st.session_state.logged_in = True

    me = api_get("/me").json()
    st.session_state.user = me

    return True, None


def register_user(mail, password, name):
    r = api_post("/register", {
        "mail": mail,
        "password": password,
        "Name": name
    })
    return (True, None) if r.ok else (False, r.text)


def guard():
    if not st.session_state.get("logged_in"):
        st.switch_page("pages/1_Login.py")
