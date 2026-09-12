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

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="LRD Recommendation",
    layout="wide"
)

st.title("LRD Recommendation & Chemical Demand Calculator")

# -------------------------------------------------------
# INPUTS
# -------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    month = st.selectbox(
        "Select Month",
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
        "Expected Production (MLD)",
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
        "Treatment Strategy",
        [
            "Auto",
            "PAC Only",
            "Alum Only"
        ]
    )

# -------------------------------------------------------
# GET MONTH TURBIDITY
# -------------------------------------------------------

turbidity_data = get_month_turbidity(month)

if turbidity_data is None:

    st.error("Unable to find month in Monthly Historical Turbidity_Pc.xlsx")
    st.stop()

normal_turbidity = turbidity_data["normal"]
elevated_turbidity = turbidity_data["elevated"]
extreme_turbidity = turbidity_data["extreme"]

# -------------------------------------------------------
# WEATHER ADJUSTMENT
# -------------------------------------------------------

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

# -------------------------------------------------------
# WATER VOLUME
# -------------------------------------------------------

days = get_days_in_month(month)

water_volume = get_water_volume(
    production,
    days
)

# -------------------------------------------------------
# KPI SECTION
# -------------------------------------------------------

st.subheader("Planning Inputs")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Month",
    month
)

k2.metric(
    "Production",
    f"{production} MLD"
)

k3.metric(
    "Days",
    days
)

k4.metric(
    "Water Volume",
    f"{water_volume:,.0f} ML"
)

# -------------------------------------------------------
# SCENARIOS
# -------------------------------------------------------

scenario_dict = {

    "Normal": normal_turbidity,
    "Elevated": elevated_turbidity,
    "Extreme": extreme_turbidity

}

dose_results = []
demand_results = []

# -------------------------------------------------------
# LOOP
# -------------------------------------------------------

for scenario, turbidity in scenario_dict.items():

    recommendation = get_lrd_recommendation(
        turbidity
    )

    s_alum = recommendation["s_alum"]
    l_alum = recommendation["l_alum"]
    p_pac = recommendation["p_pac"]
    l_pac = recommendation["l_pac"]
    polymer = recommendation["polymer"]

    # ------------------------------------
    # STRATEGY FILTER
    # ------------------------------------

    if strategy == "PAC Only":

        s_alum = 0
        l_alum = 0

    elif strategy == "Alum Only":

        p_pac = 0
        l_pac = 0

    # ------------------------------------
    # STORE DOSES
    # ------------------------------------

    dose_results.append({

        "Scenario": scenario,
        "Predicted Turbidity (NTU)": round(turbidity, 2),
        "S/Alum Dose (ppm)": s_alum,
        "L/Alum Dose (ppm)": l_alum,
        "P/PAC Dose (ppm)": p_pac,
        "L/PAC Dose (ppm)": l_pac,
        "Polymer Dose (ppm)": polymer

    })

    # ------------------------------------
    # DEMAND CALCULATION
    # ------------------------------------

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

    demand_results.append({

        "Scenario": scenario,
        "Predicted Turbidity (NTU)": round(turbidity, 2),
        "S/Alum (MT)": round(s_alum_mt, 2),
        "L/Alum (MT)": round(l_alum_mt, 2),
        "P/PAC (MT)": round(p_pac_mt, 2),
        "L/PAC (MT)": round(l_pac_mt, 2),
        "Polymer (MT)": round(polymer_mt, 2)

    })

# -------------------------------------------------------
# STRATEGY MESSAGE
# -------------------------------------------------------

st.subheader("Treatment Recommendation")

if strategy == "PAC Only":

    st.success("Recommended Treatment Strategy : PAC ONLY")

elif strategy == "Alum Only":

    st.success("Recommended Treatment Strategy : ALUM ONLY")

else:

    st.success(
        "Recommended Treatment Strategy : AUTO (Based on LRD)"
    )

# -------------------------------------------------------
# DOSE TABLE
# -------------------------------------------------------

st.subheader("Recommended Dose")

dose_df = pd.DataFrame(
    dose_results
)

st.dataframe(
    dose_df,
    use_container_width=True
)

# -------------------------------------------------------
# DEMAND TABLE
# -------------------------------------------------------

st.subheader("Chemical Demand Forecast")

demand_df = pd.DataFrame(
    demand_results
)

st.dataframe(
    demand_df,
    use_container_width=True
)

# -------------------------------------------------------
# PROCUREMENT TABLE
# -------------------------------------------------------

st.subheader("Procurement Planning Scenario")

extreme_df = demand_df[
    demand_df["Scenario"] == "Extreme"
]

st.dataframe(
    extreme_df,
    use_container_width=True
)

st.info(
    "Use the EXTREME scenario for procurement planning "
    "and safety stock calculations."
)
