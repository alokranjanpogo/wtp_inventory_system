import streamlit as st
import pandas as pd
import calendar

from utils.data_loader import (
    load_monthly_turbidity,
    load_lrd
)

st.set_page_config(layout="wide")

st.title("Chemical Demand Prediction Engine")

# -----------------------------
# Load Data
# -----------------------------

monthly_df = load_monthly_turbidity()
lrd_df = load_lrd()

# -----------------------------
# User Inputs
# -----------------------------

col1, col2, col3 = st.columns(3)

months = [
    "April","May","June","July","August",
    "September","October","November",
    "December","January","February","March"
]

with col1:
    month = st.selectbox(
        "Select Month",
        months
    )

with col2:
    production = st.number_input(
        "Expected Production (MLD)",
        min_value=200,
        max_value=235,
        value=230
    )

with col3:
    strategy = st.selectbox(
        "Coagulant Strategy",
        [
            "Auto",
            "PAC Only",
            "Alum Only",
            "Mixed"
        ]
    )

# -----------------------------
# Get Monthly Turbidity
# -----------------------------

row = monthly_df[
    monthly_df.iloc[:,0] == month
]

fy25 = float(row.iloc[0,1])
fy26 = float(row.iloc[0,2])
fy27 = float(row.iloc[0,3])

avg_turbidity = (
    fy25 + fy26 + fy27
)/3

normal_turbidity = avg_turbidity
elevated_turbidity = avg_turbidity * 1.20
extreme_turbidity = avg_turbidity * 1.50

# -----------------------------
# Function
# -----------------------------

def get_dose(turbidity):

    lrd_df["diff"] = abs(
        lrd_df["Raw_Turbidity_NTU"] - turbidity
    )

    dose_row = lrd_df.loc[
        lrd_df["diff"].idxmin()
    ]

    return dose_row


# Calendar Days

day_map = {

    "April":30,
    "May":31,
    "June":30,
    "July":31,
    "August":31,
    "September":30,
    "October":31,
    "November":30,
    "December":31,
    "January":31,
    "February":28,
    "March":31
}

days = day_map[month]

water_volume = production * days

# -----------------------------
# Scenario Calculation
# -----------------------------

scenario_data = []

scenarios = {

    "Normal": normal_turbidity,
    "Elevated": elevated_turbidity,
    "Extreme": extreme_turbidity

}

for scenario, turb in scenarios.items():

    dose = get_dose(turb)

    s_alum = float(dose["S/Alum"]) \
        if pd.notna(dose["S/Alum"]) else 0

    l_alum = float(dose["L/Alum"]) \
        if pd.notna(dose["L/Alum"]) else 0

    p_pac = float(dose["P/PAC"]) \
        if pd.notna(dose["P/PAC"]) else 0

    l_pac = float(dose["L/PAC"]) \
        if pd.notna(dose["L/PAC"]) else 0

    polymer = float(dose["Polymer"]) \
        if pd.notna(dose["Polymer"]) else 0

    # Buffer

    if scenario == "Normal":
        buffer = 1.10

    elif scenario == "Elevated":
        buffer = 1.20

    else:
        buffer = 1.30

    # Requirement

    s_alum_mt = (
        s_alum * water_volume
    ) / 1000

    l_alum_mt = (
        l_alum * water_volume
    ) / 1000

    p_pac_mt = (
        p_pac * water_volume
    ) / 1000

    l_pac_mt = (
        l_pac * water_volume
    ) / 1000

    polymer_mt = (
        polymer * water_volume
    ) / 1000

    s_alum_mt *= buffer
    l_alum_mt *= buffer
    p_pac_mt *= buffer
    l_pac_mt *= buffer
    polymer_mt *= buffer

    scenario_data.append({

        "Scenario": scenario,
        "Turbidity NTU": round(turb,2),
        "S/Alum MT": round(s_alum_mt,2),
        "L/Alum MT": round(l_alum_mt,2),
        "P/PAC MT": round(p_pac_mt,2),
        "L/PAC MT": round(l_pac_mt,2),
        "Polymer MT": round(polymer_mt,2)

    })

# -----------------------------
# KPI
# -----------------------------

st.subheader("Prediction Inputs")

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Month",
    month
)

c2.metric(
    "Production",
    f"{production} MLD"
)

c3.metric(
    "Days",
    days
)

c4.metric(
    
