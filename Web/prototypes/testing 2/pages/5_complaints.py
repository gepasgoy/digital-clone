import streamlit as st
from auth import check_auth
from api_client import add_complaint
check_auth()

st.title("📝 Жалобы")
patient_id = st.number_input("ID пациента", min_value=1, step=1, value=1)
description = st.text_area("Описание жалобы", height=150)

if st.button("Отправить жалобу"):
    if not description:
        st.error("Введите описание жалобы")
    else:
        result = add_complaint(patient_id, description)
        if result["success"]:
            st.success(result["data"]["message"])
        else:
            st.error(result["message"])

if st.button("Назад"):
    st.switch_page("pages/1.py")