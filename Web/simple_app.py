import streamlit as st
import requests
import warnings

# Отключаем предупреждения Streamlit
warnings.filterwarnings("ignore", message="missing ScriptRunContext")
st.title("🔐 Простейшая авторизация")


# Поля для ввода
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Кнопка входа
if st.button("Login"):
    if username and password:
        try:
            # Отправляем запрос к API
            response = requests.post(
                "http://localhost:8000/login", 
                json={"username": username, "password": password}
            )
            
            result = response.json()
            
            if result["success"]:
                st.success(result["message"])
                st.balloons()  # Анимация при успешном входе
                
                # Показать защищенный контент
                st.markdown("---")
                st.subheader("Добро пожаловать в систему!")
                st.write("Вы успешно авторизовались.")
                st.write("Здесь может быть ваш защищенный контент.")
            else:
                st.error(result["message"])
                
        except requests.exceptions.ConnectionError:
            st.error("Не удалось подключиться к серверу. Убедитесь, что FastAPI запущен!")
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Пожалуйста, введите логин и пароль")

# Информация о тестовых пользователях
st.sidebar.markdown("### Тестовые пользователи")
st.sidebar.write("**admin** / **admin123**")
st.sidebar.write("**user** / **password**")

# Инструкция
st.sidebar.markdown("### Как запустить:")
st.sidebar.code("""
# Терминал 1:
uvicorn simple_api:app --reload

# Терминал 2:
streamlit run simple_app.py
""")