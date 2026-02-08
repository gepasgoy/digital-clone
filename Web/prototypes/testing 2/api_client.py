import requests
import streamlit as st

BASE_URL = "http://localhost:8000"

def api_request(method, endpoint, data=None, params=None):
    try:
        cookies = st.session_state.get("cookies", {})
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
        
        response = requests.request(
            method=method,
            url=f"{BASE_URL}/{endpoint}",
            json=data,
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.json().get("detail", "Ошибка запроса")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def login(email, password):
    try:
        response = requests.post(f"{BASE_URL}/login", json={"mail": email, "password": password}, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def register_user(email, password, name):
    return api_request("POST", "register", {"mail": email, "password": password, "Name": name})

get_medical_card = lambda pid=None: api_request("GET", "medical-card", params={"patient_id": pid} if pid else None)
add_pulse_monitoring = lambda value, pid=None: api_request("POST", "pulse-monitoring", {"value": value, "patient_id": pid} if pid else {"value": value})
add_complaint = lambda pid, desc: api_request("POST", "sub_complains", {"PatientId": pid, "Description": desc})
get_notifications = lambda: api_request("GET", "notifications")
logout = lambda: api_request("POST", "logout")
refresh_token = lambda: api_request("POST", "refresh")