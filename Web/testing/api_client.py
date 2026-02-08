import requests
import streamlit as st

API = "http://localhost:8000"


def _headers():
    if "token" in st.session_state:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def api_get(path):
    r = requests.get(API + path, headers=_headers())

    if r.status_code == 401:
        if refresh():
            r = requests.get(API + path, headers=_headers())

    return r


def api_post(path, json=None):
    r = requests.post(API + path, json=json, headers=_headers())

    if r.status_code == 401:
        if refresh():
            r = requests.post(API + path, json=json, headers=_headers())

    return r


def refresh():
    if "refresh_token" not in st.session_state:
        logout_local()
        return False

    r = requests.post(API + "/refresh",
        headers={"Authorization": f"Bearer {st.session_state.token}"}
    )

    if not r.ok:
        logout_local()
        return False

    st.session_state.token = r.json()["access_token"]
    return True


def logout_local():
    st.session_state.clear()
