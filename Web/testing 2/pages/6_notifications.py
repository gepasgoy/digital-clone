import streamlit as st
from auth import check_auth
from api_client import get_notifications

check_auth()

st.title("🔔 Уведомления")

if st.button("Проверить уведомления"):
    result = get_notifications()
    
    if result["success"]:
        data = result["data"]
        
        st.metric("Всего уведомлений", data["total_notifications"])
        
        if data["notifications"]:
            for i, notification in enumerate(data["notifications"], 1):
                # Определяем цвет в зависимости от приоритета
                if notification["priority"] == "high":
                    st.error(f"🚨 **Высокий приоритет**: {notification['message']}")
                elif notification["priority"] == "medium":
                    st.warning(f"⚠️ **Средний приоритет**: {notification['message']}")
                else:
                    st.info(f"ℹ️ **Низкий приоритет**: {notification['message']}")
                
                if notification["action_required"]:
                    st.write("Требуется действие!")
                
                st.divider()
        else:
            st.success("Нет новых уведомлений")
    else:
        st.error(result["message"])

if st.button("Назад"):
    st.switch_page("pages/1.py")