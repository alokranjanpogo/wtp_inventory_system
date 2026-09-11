import streamlit as st

from utils.data_loader import (
    load_daily_turbidity
)

df = load_daily_turbidity()

st.title(
    "Turbidity Analytics"
)

st.write(df.head())

st.write(
    "Rows:",
    df.shape[0]
)

st.write(
    "Columns:",
    list(df.columns)
)
