import streamlit as st
from auth import check_auth
from api_client import add_pulse_monitoring
check_auth()

st.title("❤️ Мониторинг пульса")
value = st.number_input("Значение пульса (уд/мин)", min_value=30, max_value=300, value=70)
patient_id = st.number_input("ID пациента (оставьте пустым для себя)", min_value=1, step=1, value=None)

if st.button("Сохранить измерение"):
    if not value:
        st.error("Введите значение пульса")
    else:
        result = add_pulse_monitoring(value, patient_id)
        if result["success"]:
            st.success(result["data"]["message"])
        else:
            st.error(result["message"])

if st.button("Назад"):
    st.switch_page("pages/1.py")