import streamlit as st

from utils.lrd_engine import (
    get_recommended_dose
)

st.title(
    "LRD Recommendation"
)

turbidity = st.number_input(
    "Enter Turbidity",
    min_value=0.0,
    value=20.0
)

if st.button(
        "Get Recommendation"
):

    result = get_recommended_dose(
        turbidity
