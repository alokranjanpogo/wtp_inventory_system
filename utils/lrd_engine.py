import pandas as pd
import calendar

from utils.data_loader import (
    load_lrd,
    load_monthly_turbidity
)


# ==========================================================
# SAFE FLOAT
# ==========================================================

def safe_float(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


# ==========================================================
# MONTH TURBIDITY LOGIC
# ==========================================================

def get_month_turbidity(
    month,
    exclude_outlier=True
):

    monthly_df = load_monthly_turbidity()

    row = monthly_df[
        monthly_df.iloc[:, 0]
        .astype(str)
        .str.strip()
        == month
    ]

    if row.empty:
        return None

    values = []

    for col in row.columns[1:4]:

        value = pd.to_numeric(
            row.iloc[0][col],
            errors="coerce"
        )

        if pd.notna(value):
            values.append(float(value))

    values.sort()

    working_values = values.copy()

    # -------------------------------------------------
    # SIMPLE OUTLIER LOGIC
    # -------------------------------------------------

    if exclude_outlier and len(values) == 3:

        low = values[0]
        mid = values[1]
        high = values[2]

        lower_gap = mid - low
        upper_gap = high - mid

        if lower_gap > 0:

            if upper_gap > (lower_gap * 1.5):

                working_values.remove(high)

    if len(working_values) == 0:
        working_values = values

    # -------------------------------------------------
    # EXPECTED
    # -------------------------------------------------

    expected = round(
        sum(working_values)
        / len(working_values),
        2
    )

    # -------------------------------------------------
    # VARIABILITY
    # -------------------------------------------------

    variability = round(
        max(working_values)
        - min(working_values),
        2
    )

    # -------------------------------------------------
    # PLANNING
    # -------------------------------------------------

    planning = round(
        expected
        + (variability * 0.15),
        2
    )

    # -------------------------------------------------
    # EMERGENCY
    # -------------------------------------------------

    emergency = round(
        expected
        + (variability * 0.30),
        2
    )

    return {

        "raw_values": values,

        "working_values": working_values,

        "expected": expected,

        "planning": planning,

        "emergency": emergency,

        "variability": variability

    }


# ==========================================================
# WEATHER ADJUSTMENT
# ==========================================================

def apply_weather_adjustment(
    turbidity,
    weather_risk
):

    weather_factors = {

        "Low": 1.00,
        "Moderate": 1.05,
        "High": 1.10

    }

    factor = weather_factors.get(
        weather_risk,
        1.00
    )

    return round(
        turbidity * factor,
        2
    )


# ==========================================================
# LRD LOOKUP
# ==========================================================

def get_lrd_recommendation(
    turbidity
):

    lrd_df = load_lrd().copy()

    lrd_df["Raw_Turbidity_NTU"] = pd.to_numeric(
        lrd_df["Raw_Turbidity_NTU"],
        errors="coerce"
    )

    lrd_df = lrd_df.dropna(
        subset=["Raw_Turbidity_NTU"]
    )

    lrd_df["Difference"] = abs(
        lrd_df["Raw_Turbidity_NTU"]
        - turbidity
    )

    row = lrd_df.sort_values(
        "Difference"
    ).iloc[0]

    return {

        "matched_turbidity":
            safe_float(
                row["Raw_Turbidity_NTU"]
            ),

        "s_alum":
            safe_float(
                row["S/Alum"]
            ),

        "l_alum":
            safe_float(
                row["L/Alum"]
            ),

        "p_pac":
            safe_float(
                row["P/PAC"]
            ),

        "l_pac":
            safe_float(
                row["L/PAC"]
            ),

        "polymer":
            safe_float(
                row["Polymer"]
            )

    }


# ==========================================================
# AUTO STRATEGY
# ==========================================================

def get_auto_strategy(
    recommendation
):

    pac_total = (
        recommendation["p_pac"]
        +
        recommendation["l_pac"]
    )

    alum_total = (
        recommendation["s_alum"]
        +
        recommendation["l_alum"]
    )

    if pac_total > alum_total:
        return "PAC"

    elif alum_total > pac_total:
        return "ALUM"

    else:
        return "MIXED"


# ==========================================================
# DAYS IN MONTH
# ==========================================================

def get_days_in_month(
    month_name,
    year=2026
):

    month_map = {

        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12

    }

    month_number = month_map[
        month_name
    ]

    return calendar.monthrange(
        year,
        month_number
    )[1]


# ==========================================================
# WATER VOLUME
# ==========================================================

def get_water_volume(
    production_mld,
    days
):

    return production_mld * days


# ==========================================================
# CHEMICAL DEMAND
# ppm × ML = kg
# kg / 1000 = MT
# ==========================================================

def chemical_mt_from_dose(
    dose_ppm,
    water_volume
):

    kg = dose_ppm * water_volume

    mt = kg / 1000

    return round(
        mt,
        2
    )


# ==========================================================
# PROCUREMENT BUFFER
# ==========================================================

def procurement_quantity(
    quantity_mt,
    buffer_percent=15
):

    return round(
        quantity_mt
        * (
            1 +
            buffer_percent / 100
        ),
        2
    )
