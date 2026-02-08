import requests
import streamlit as st

# Базовый URL вашего API
BASE_URL = "http://localhost:8000"  # Измените на адрес вашего API

def login(email, password):
    """Аутентификация пользователя"""
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"mail": email, "password": password},
            timeout=10
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def register_user(email, password, name):
    """Регистрация пользователя"""
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"mail": email, "password": password, "Name": name},
            timeout=10
        )
        if response.status_code == 200:
            return {"success": True, "message": "Регистрация успешна"}
        else:
            return {"success": False, "message": response.json().get("detail", "Ошибка регистрации")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def get_medical_card(patient_id=None):
    """Получение медицинской карты"""
    try:
        cookies = st.session_state.get("cookies", {})
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
        
        params = {}
        if patient_id:
            params["patient_id"] = patient_id
            
        response = requests.get(
            f"{BASE_URL}/medical-card",
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": response.json().get("detail", "Ошибка получения данных")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def add_pulse_monitoring(value, patient_id=None):
    """Добавление данных пульса"""
    try:
        cookies = st.session_state.get("cookies", {})
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
        
        data = {"value": value}
        if patient_id:
            data["patient_id"] = patient_id
            
        response = requests.post(
            f"{BASE_URL}/pulse-monitoring",
            json=data,
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": response.json().get("detail", "Ошибка сохранения")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def add_complaint(patient_id, description):
    """Добавление жалоб"""
    try:
        cookies = st.session_state.get("cookies", {})
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
        
        response = requests.post(
            f"{BASE_URL}/sub_complains",
            json={"PatientId": patient_id, "Description": description},
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": response.json().get("detail", "Ошибка сохранения")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def get_notifications():
    """Получение уведомлений"""
    try:
        cookies = st.session_state.get("cookies", {})
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
        
        response = requests.get(
            f"{BASE_URL}/notifications",
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": response.json().get("detail", "Ошибка получения уведомлений")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def logout():
    """Выход из системы"""
    try:
        cookies = st.session_state.get("cookies", {})
        response = requests.post(
            f"{BASE_URL}/logout",
            cookies=cookies,
            timeout=10
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Ошибка соединения: {str(e)}"}

def refresh_token():
    """Обновление токена"""
    try:
        cookies = st.session_state.get("cookies", {})
        response = requests.post(
            f"{BASE_URL}/refresh",
            cookies=cookies,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state["access_token"] = data.get("access_token")
            return {"success": True}
        else:
            return {"success": False}
    except requests.exceptions.RequestException:
        return {"success": False}