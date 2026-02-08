import streamlit as st
from auth import check_auth
from api_client import logout

check_auth()

st.title("🏠 Главная")
st.write(f"Вы вошли как: **{st.session_state.user}**")

st.sidebar.title("📋 Меню")
for btn, page in [("👤 Профиль", "2.py"), ("🏥 Медицинская карта", "3_medical_card.py"), 
                  ("❤️ Мониторинг пульса", "4_pulse_monitoring.py"), ("📝 Жалобы", "5_complaints.py"), 
                  ("🔔 Уведомления", "6_notifications.py")]:
    if st.sidebar.button(btn):
        st.switch_page(f"pages/{page}")

if st.sidebar.button("🚪 Выход"):
    logout()
    from auth import clear_auth
    clear_auth()
    st.success("Выход выполнен успешно")
    st.rerun()

col1, col2, col3 = st.columns(3)
col1.metric("Пользователь", st.session_state.user)
col2.metric("Статус", "Активен")
col3.metric("Доступ", "Полный")

if st.button("📊 Добавить измерение пульса", use_container_width=True):
    st.switch_page("pages/4_pulse_monitoring.py")
if st.button("📝 Добавить жалобу", use_container_width=True):
    st.switch_page("pages/5_complaints.py")