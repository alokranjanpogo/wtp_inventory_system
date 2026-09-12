import streamlit as st
import pandas as pd

from utils.lrd_engine import (
    get_month_turbidity,
    apply_weather_adjustment,
    get_lrd_recommendation,
    get_days_in_month,
    get_water_volume,
    chemical_mt_from_dose,
    apply_buffer
)

st.set_page_config(
    page_title="LRD Recommendation",
    layout="wide"
)

st.title("LRD Recommendation & Chemical Demand Calculator")

# =====================================================
# INPUTS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    month = st.selectbox(
        "Month",
        [
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
            "January",
            "February",
            "March"
        ]
    )

with col2:

    production = st.number_input(
        "Production (MLD)",
        min_value=200,
        max_value=235,
        value=230
    )

with col3:

    weather_risk = st.selectbox(
        "Weather Risk",
        [
            "Low",
            "Moderate",
            "High"
        ]
    )

with col4:

    strategy = st.selectbox(
        "Strategy",
        [
            "Auto",
            "PAC Only",
            "Alum Only"
        ]
    )

# =====================================================
# TURBIDITY SCENARIOS
# =====================================================

turbidity_data = get_month_turbidity(month)

if turbidity_data is None:

    st.error("Month data not found.")
    st.stop()

normal_turbidity = turbidity_data["normal"]
elevated_turbidity = turbidity_data["elevated"]
extreme_turbidity = turbidity_data["extreme"]

# Weather correction

normal_turbidity = apply_weather_adjustment(
    normal_turbidity,
    weather_risk
)

elevated_turbidity = apply_weather_adjustment(
    elevated_turbidity,
    weather_risk
)

extreme_turbidity = apply_weather_adjustment(
    extreme_turbidity,
    weather_risk
)

# =====================================================
# DAYS & WATER VOLUME
# =====================================================

days = get_days_in_month(month)

water_volume = get_water_volume(
    production,
    days
)

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("Planning Inputs")

c1, c2, c3, c4 = st.columns(4)

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
    "Water Volume",
    f"{water_volume:,.0f} ML"
)

# =====================================================
# CALCULATIONS
# =====================================================

results = []

scenario_dict = {

    "Normal": normal_turbidity,
    "Elevated": elevated_turbidity,
    "Extreme": extreme_turbidity

}

for scenario, turbidity in scenario_dict.items():

    recommendation = get_lrd_recommendation(
        turbidity
    )

    s_alum = recommendation["s_alum"]
    l_alum = recommendation["l_alum"]
    p_pac = recommendation["p_pac"]
    l_pac = recommendation["l_pac"]
    polymer = recommendation["polymer"]

    # =================================================
    # STRATEGY
    # =================================================

    if strategy == "PAC Only":

        s_alum = 0
        l_alum = 0

    elif strategy == "Alum Only":

        p_pac = 0
        l_pac = 0

    # =================================================
    # QUANTITY CALCULATION
    # =================================================

    s_alum_mt = chemical_mt_from_dose(
        s_alum,
        water_volume
    )

    l_alum_mt = chemical_mt_from_dose(
        l_alum,
        water_volume
    )

    p_pac_mt = chemical_mt_from_dose(
        p_pac,
        water_volume
    )

    l_pac_mt = chemical_mt_from_dose(
        l_pac,
        water_volume
    )

    polymer_mt = chemical_mt_from_dose(
        polymer,
        water_volume
    )

    s_alum_mt = apply_buffer(
        s_alum_mt,
        scenario
    )

    l_alum_mt = apply_buffer(
        l_alum_mt,
        scenario
    )

    p_pac_mt = apply_buffer(
        p_pac_mt,
        scenario
    )

    l_pac_mt = apply_buffer(
        l_pac_mt,
        scenario
    )

    polymer_mt = apply_buffer(
        polymer_mt,
        scenario
    )

    results.append({

        "Scenario": scenario,

        "Predicted Turbidity (NTU)":
            round(turbidity, 2),

        "S/Alum (MT)":
            round(s_alum_mt, 2),

        "L/Alum (MT)":
            round(l_alum_mt, 2),

        "P/PAC (MT)":
            round(p_pac_mt, 2),

        "L/PAC (MT)":
            round(l_pac_mt, 2),

        "Polymer (MT)":
            round(polymer_mt, 2)

    })

# =====================================================
# DISPLAY RESULTS
# =====================================================

st.subheader("Chemical Demand Forecast")

forecast_df = pd.DataFrame(results)

st.dataframe(
    forecast_df,
    use_container_width=True
)

# =====================================================
# RECOMMENDATION
# =====================================================

st.subheader("Planning Recommendation")

extreme_row = forecast_df[
    forecast_df["Scenario"] == "Extreme"
]

st.info(
    "For procurement planning, keep stock "
    "equal to or higher than the EXTREME "
    "scenario demand."
)

st.dataframe(
    extreme_row,
    use_container_width=True
)
