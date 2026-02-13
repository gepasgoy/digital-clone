import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="wide")

st.title("📊 Test Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Users", random.randint(100, 500))
col2.metric("Orders", random.randint(50, 200))
col3.metric("Errors", random.randint(0, 10))

st.divider()

data = pd.DataFrame({
    "value": [random.randint(1, 100) for _ in range(20)]
})

st.line_chart(data)
st.dataframe(data, use_container_width=True)
