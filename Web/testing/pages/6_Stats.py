import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from auth import guard
from ui import topbar

#импорт для экспорта данных(не уверен, стоит ли делать)
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table

guard()
topbar()

st.title("Статистика")

# 📊 MOCK ДАННЫЕ ДАВЛЕНИЯ (заменишь на API потом)

days = 30
dates = pd.date_range(datetime.now() - timedelta(days=days), periods=days)

df = pd.DataFrame({
    "date": dates,
    "sys": np.random.randint(110, 150, size=days),  # верхнее
    "dia": np.random.randint(70, 95, size=days),    # нижнее
})

# 🎛 ВЫБОР ПЕРИОДА

period = st.selectbox(
    "Период",
    ["7 дней", "14 дней", "30 дней"]
)

cut = {
    "7 дней": 7,
    "14 дней": 14,
    "30 дней": 30
}[period]

df = df.tail(cut).set_index("date")

# 📈 ДВОЙНОЙ ГРАФИК

st.subheader("Артериальное давление")

st.line_chart(df[["sys", "dia"]])

# ✅ ЗОНЫ НОРМЫ

st.caption("Нормы:")
c1, c2, c3 = st.columns(3)

with c1:
    st.success("Систолическое: 90–120")

with c2:
    st.success("Диастолическое: 60–80")

with c3:
    st.warning("Выше — повод проверить")

# 📌 СВОДКА

st.metric("Среднее SYS", int(df["sys"].mean()))
st.metric("Среднее DIA", int(df["dia"].mean()))



#///необязательно
st.subheader("Экспорт данных")

export_df = df.reset_index()

c1, c2, c3 = st.columns(3)

# CSV

with c1:
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "CSV",
        csv,
        file_name="pressure.csv",
        use_container_width=True
    )

# XLSX

with c2:
    xbuf = BytesIO()
    export_df.to_excel(xbuf, index=False)
    st.download_button(
        "XLSX",
        xbuf.getvalue(),
        file_name="pressure.xlsx",
        use_container_width=True
    )

# PDF

with c3:
    pbuf = BytesIO()
    doc = SimpleDocTemplate(pbuf, pagesize=A4)

    table_data = [export_df.columns.tolist()] + export_df.values.tolist()
    table = Table(table_data)

    doc.build([table])

    st.download_button(
        "PDF",
        pbuf.getvalue(),
        file_name="pressure.pdf",
        use_container_width=True
    )

