import streamlit as st
from auth import check_auth
from api_client import get_medical_card

check_auth()

st.title("🏥 Медицинская карта")

patient_id = st.number_input("ID пациента (оставьте пустым для своей карты)", 
                           min_value=1, step=1, value=None)

if st.button("Загрузить медицинскую карту"):
    result = get_medical_card(patient_id)
    
    if result["success"]:
        data = result["data"]
        
        # Информация о пациенте
        st.subheader("👤 Информация о пациенте")
        patient_info = data["patient_info"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ID", patient_info["id"])
        with col2:
            st.metric("ФИО", patient_info["full_name"])
        with col3:
            st.metric("Возраст", patient_info["age"])
        
        # Исследования
        if data["research"]:
            st.subheader("🔬 Медицинские исследования")
            for research in data["research"]:
                with st.expander(f"{research['name']} - {research['date']}"):
                    st.write(f"**Статус:** {research['state']}")
                    st.write(f"**Результат:** {research['result']}")
        else:
            st.info("Нет данных об исследованиях")
        
        # Мониторинг пульса
        if data["pulse_monitoring"]:
            st.subheader("📊 Мониторинг пульса")
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data["pulse_monitoring"])
            df['date'] = pd.to_datetime(df['date'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df[['date', 'value']], use_container_width=True)
            with col2:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(df['date'], df['value'], marker='o')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Пульс (уд/мин)')
                ax.set_title('График пульса')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        else:
            st.info("Нет данных мониторинга пульса")
    else:
        st.error(result["message"])

if st.button("Назад"):
    st.switch_page("pages/1.py")