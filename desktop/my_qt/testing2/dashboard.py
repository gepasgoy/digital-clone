import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

page = st.query_params.get("page", "overview")

if page == "overview":
    st.title("Медицинский аналитический дашборд")

    st.subheader("📈 Эффективность лечения")
    days = pd.date_range("2026-01-01", periods=14)
    treatment_df = pd.DataFrame({
        "Дата": days,
        "Среднее давление": np.linspace(165, 130, 14) + np.random.randint(-3, 3, 14),
        "Глюкоза": np.linspace(9.2, 6.1, 14) + np.random.normal(0, 0.2, 14),
        "CRP": np.linspace(18, 5, 14) + np.random.normal(0, 1, 14),
    })
    col1, col2, col3 = st.columns(3)
    col1.metric("АД текущее", "132", "-33")
    col2.metric("Глюкоза", "6.3", "-2.9")
    col3.metric("CRP", "6", "-12")
    fig = px.line(treatment_df, x="Дата", y=["Среднее давление", "Глюкоза", "CRP"],
                  title="Динамика клинических показателей")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧬 Статистика заболеваний")
    disease_df = pd.DataFrame({
        "Нозология": ["Гипертония", "СД 2 типа", "ИБС", "ОРВИ", "Бронхит", "Астма"],
        "Пациентов": [120, 85, 64, 210, 43, 27]
    })
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(disease_df, names="Нозология", values="Пациентов", title="Распределение пациентов")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(disease_df, x="Нозология", y="Пациентов", title="Количество случаев")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🩺 Рабочая нагрузка")
    work_df = pd.DataFrame({
        "День": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
        "Приемов": [28, 34, 31, 40, 37, 18],
        "Первичных": [10, 12, 11, 15, 13, 6],
        "Повторных": [18, 22, 20, 25, 24, 12],
    })
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего приемов", sum(work_df["Приемов"]))
    col2.metric("Среднее/день", round(work_df["Приемов"].mean(), 1))
    col3.metric("Максимум", max(work_df["Приемов"]))
    fig = px.bar(work_df, x="День", y=["Первичных", "Повторных"],
                 title="Структура приемов по дням", barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

elif page == "analytics":
    st.title("Аналитические отчеты по эффективности лечения")

    st.subheader("Динамика эффективности лечения")
    df = pd.DataFrame({
        "Месяц": ["Янв", "Фев", "Мар", "Апр"],
        "Процент улучшений": [75, 78, 82, 80],
        "Плановый показатель": [80, 80, 80, 80]
    })
    fig = px.line(df, x="Месяц", y=["Процент улучшений", "Плановый показатель"],
                  title="Сравнение с планом")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Распределение исходов")
    outcomes = pd.DataFrame({
        "Исход": ["Выздоровление", "Улучшение", "Без изменений", "Ухудшение"],
        "Количество": [45, 30, 15, 10]
    })
    fig = px.pie(outcomes, names="Исход", values="Количество", title="Исходы лечения")
    st.plotly_chart(fig, use_container_width=True)