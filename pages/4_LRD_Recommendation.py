import streamlit as st
import pandas as pd

from utils.lrd_engine import (
    get_month_turbidity,
    apply_weather_adjustment,
    get_lrd_recommendation,
    get_auto_strategy,
    get_days_in_month,
    get_water_volume,
    chemical_mt_from_dose,
    procurement_quantity
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="LRD Recommendation",
    layout="wide"
)

st.title(
    "LRD Recommendation & Chemical Demand Calculator"
)

# =====================================================
# INPUTS
# =====================================================

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
        "Production (MLD)",
        min_value=180,
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
            "Alum Only",
            "Mixed"
        ]
    )

exclude_outlier = st.checkbox(
    "Exclude Outlier",
    value=True
)

mix_ratio = 70

if strategy == "Mixed":

    mix_ratio = st.slider(
        "PAC Contribution (%)",
        0,
        100,
        70
    )

# =====================================================
# TURBIDITY MODEL
# =====================================================

turbidity_data = get_month_turbidity(
    month,
    exclude_outlier
)

if turbidity_data is None:

    st.error(
        "Month data not available"
    )

    st.stop()

expected_turbidity = turbidity_data["expected"]

planning_turbidity = turbidity_data["planning"]

emergency_turbidity = turbidity_data["emergency"]

# =====================================================
# WEATHER ADJUSTMENT
# =====================================================

expected_turbidity = apply_weather_adjustment(
    expected_turbidity,
    weather_risk
)

planning_turbidity = apply_weather_adjustment(
    planning_turbidity,
    weather_risk
)

emergency_turbidity = apply_weather_adjustment(
    emergency_turbidity,
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
# KPI
# =====================================================

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

# =====================================================
# HISTORICAL ANALYSIS
# =====================================================

st.subheader(
    "Historical Turbidity Analysis"
)

c1, c2 = st.columns(2)

with c1:

    st.write(
        "Original Historical Values"
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Turbidity":
                turbidity_data[
                    "raw_values"
                ]
            }
        ),
        use_container_width=True
    )

with c2:

    st.write(
        "Values Used For Prediction"
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Turbidity":
                turbidity_data[
                    "working_values"
                ]
            }
        ),
        use_container_width=True
    )

# =====================================================
# SCENARIOS
# =====================================================

scenario_df = pd.DataFrame({

    "Scenario": [
        "Expected",
        "Planning",
        "Emergency"
    ],

    "Predicted Turbidity (NTU)": [

        expected_turbidity,

        planning_turbidity,

        emergency_turbidity

    ]

})

st.subheader(
    "Predicted Turbidity"
)

st.dataframe(
    scenario_df,
    use_container_width=True
)

# =====================================================
# PROCESS
# =====================================================

dose_results = []

demand_results = []

for scenario, turbidity in zip(

    scenario_df["Scenario"],

    scenario_df[
        "Predicted Turbidity (NTU)"
    ]

):

    recommendation = get_lrd_recommendation(
        turbidity
    )

    s_alum = recommendation["s_alum"]

    l_alum = recommendation["l_alum"]

    p_pac = recommendation["p_pac"]

    l_pac = recommendation["l_pac"]

    polymer = recommendation["polymer"]

    auto_strategy = get_auto_strategy(
        recommendation
    )

    # ==========================================
    # STRATEGY
    # ==========================================

    if strategy == "PAC Only":

        s_alum = 0
        l_alum = 0

    elif strategy == "Alum Only":

        p_pac = 0
        l_pac = 0

    elif strategy == "Mixed":

        pac_factor = (
            mix_ratio / 100
        )

        alum_factor = (
            1 -
            pac_factor
        )

        p_pac = p_pac * pac_factor

        l_pac = l_pac * pac_factor

        s_alum = s_alum * alum_factor

        l_alum = l_alum * alum_factor

    elif strategy == "Auto":

        if auto_strategy == "PAC":

            s_alum = 0
            l_alum = 0

        elif auto_strategy == "ALUM":

            p_pac = 0
            l_pac = 0

    dose_results.append({

        "Scenario": scenario,

        "Turbidity":

        turbidity,

        "S/Alum Dose":

        round(s_alum, 2),

        "L/Alum Dose":

        round(l_alum, 2),

        "P/PAC Dose":

        round(p_pac, 2),

        "L/PAC Dose":

        round(l_pac, 2),

        "Polymer Dose":

        round(polymer, 3)

    })

    demand_results.append({

        "Scenario": scenario,

        "S/Alum (MT)":

        chemical_mt_from_dose(
            s_alum,
            water_volume
        ),

        "L/Alum (MT)":

        chemical_mt_from_dose(
            l_alum,
            water_volume
        ),

        "P/PAC (MT)":

        chemical_mt_from_dose(
            p_pac,
            water_volume
        ),

        "L/PAC (MT)":

        chemical_mt_from_dose(
            l_pac,
            water_volume
        ),

        "Polymer (MT)":

        chemical_mt_from_dose(
            polymer,
            water_volume
        )

    })

# =====================================================
# STRATEGY MESSAGE
# =====================================================

if strategy == "Auto":

    st.success(
        "AUTO strategy is using LRD recommendation."
    )

elif strategy == "PAC Only":

    st.info(
        "PAC based treatment selected."
    )

elif strategy == "Alum Only":

    st.info(
        "Alum based treatment selected."
    )

else:

    st.info(
        f"Mixed Strategy : {mix_ratio}% PAC"
    )

# =====================================================
# DOSE TABLE
# =====================================================

st.subheader(
    "Recommended Dosage"
)

dose_df = pd.DataFrame(
    dose_results
)

st.dataframe(
    dose_df,
    use_container_width=True
)

# =====================================================
# DEMAND TABLE
# =====================================================

st.subheader(
    "Chemical Demand Forecast"
)

demand_df = pd.DataFrame(
    demand_results
)

st.dataframe(
    demand_df,
    use_container_width=True
)

# =====================================================
# PROCUREMENT
# =====================================================

planning_df = demand_df[
    demand_df["Scenario"]
    == "Planning"
].copy()

chemical_cols = [

    "S/Alum (MT)",
    "L/Alum (MT)",
    "P/PAC (MT)",
    "L/PAC (MT)",
    "Polymer (MT)"

]

for col in chemical_cols:

    planning_df[col] = planning_df[col].apply(
        lambda x: procurement_quantity(
            x,
            15
        )
    )

planning_df["Scenario"] = (
    "Recommended Procurement"
)

st.subheader(
    "Recommended Procurement Quantity"
)

st.dataframe(
    planning_df,
    use_container_width=True
)

st.success(
    "Procurement Quantity = Planning Demand + 15% Buffer"
)
