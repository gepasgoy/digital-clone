import streamlit as st
from auth import check_auth
from api_client import logout

check_auth()

st.title("🏠 Главная")
st.write(f"Вы вошли как: **{st.session_state.user}**")

# Создаем меню навигации
st.sidebar.title("📋 Меню")

if st.sidebar.button("👤 Профиль"):
    st.switch_page("pages/2.py")

if st.sidebar.button("🏥 Медицинская карта"):
    st.switch_page("pages/3_medical_card.py")

if st.sidebar.button("❤️ Мониторинг пульса"):
    st.switch_page("pages/4_pulse_monitoring.py")

if st.sidebar.button("📝 Жалобы"):
    st.switch_page("pages/5_complaints.py")

if st.sidebar.button("🔔 Уведомления"):
    st.switch_page("pages/6_notifications.py")

if st.sidebar.button("🚪 Выход"):
    logout_result = logout()
    from auth import clear_auth
    clear_auth()
    st.success("Выход выполнен успешно")
    st.rerun()

# Основной контент
st.write("### Добро пожаловать в медицинскую информационную систему!")
st.write("Используйте меню слева для навигации по функциям системы.")

# Краткая статистика
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Пользователь", st.session_state.user)
with col2:
    st.metric("Статус", "Активен")
with col3:
    st.metric("Доступ", "Полный")

st.divider()
st.write("### Быстрый доступ")
quick_col1, quick_col2 = st.columns(2)
with quick_col1:
    if st.button("📊 Добавить измерение пульса", use_container_width=True):
        st.switch_page("pages/4_pulse_monitoring.py")
with quick_col2:
    if st.button("📝 Добавить жалобу", use_container_width=True):
        st.switch_page("pages/5_complaints.py")