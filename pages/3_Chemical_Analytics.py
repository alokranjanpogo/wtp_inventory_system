import streamlit as st

from utils.data_loader import (
    load_chemical_consumption
)

df = load_chemical_consumption()

st.title(
    "Chemical Analytics"
)

st.write(df.head())

st.write(df.shape)
