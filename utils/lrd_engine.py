import pandas as pd
import calendar

from utils.data_loader import (
    load_lrd,
    load_monthly_turbidity
)


# --------------------------------------------------
# Get Month Turbidity Statistics
# --------------------------------------------------

def get_month_turbidity(month):

    monthly_df = load_monthly_turbidity()

    row = monthly_df[
        monthly_df.iloc[:, 0].astype(str).str.strip()
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
            values.append(value)

    values = sorted(values)

    return {

        "normal": values[1],      # median

        "elevated": round(
            sum(values) / len(values),
            2
        ),

        "extreme": max(values)

    }


# --------------------------------------------------
# Weather Correction
# --------------------------------------------------

def apply_weather_adjustment(
        turbidity,
        weather_risk
):

    weather_risk = weather_risk.lower()

    if weather_risk == "low":

        return turbidity

    elif weather_risk == "moderate":

        return turbidity * 1.10

    elif weather_risk == "high":

        return turbidity * 1.20

    return turbidity


# --------------------------------------------------
# Nearest LRD Match
# --------------------------------------------------

def get_lrd_recommendation(
        turbidity
):

    lrd_df = load_lrd().copy()

    turbidity_col = "Raw_Turbidity_NTU"

    lrd_df[turbidity_col] = pd.to_numeric(
        lrd_df[turbidity_col],
        errors="coerce"
    )

    lrd_df = lrd_df.dropna(
        subset=[turbidity_col]
    )

    lrd_df["diff"] = abs(
        lrd_df[turbidity_col]
        - turbidity
    )

    row = lrd_df.sort_values(
        "diff"
    ).iloc[0]

    return {

        "turbidity": row["Raw_Turbidity_NTU"],

        "s_alum": pd.to_numeric(
            row.get("S/Alum", 0),
            errors="coerce"
        ),

        "l_alum": pd.to_numeric(
            row.get("L/Alum", 0),
            errors="coerce"
        ),

        "p_pac": pd.to_numeric(
            row.get("P/PAC", 0),
            errors="coerce"
        ),

        "l_pac": pd.to_numeric(
            row.get("L/PAC", 0),
            errors="coerce"
        ),

        "polymer": pd.to_numeric(
            row.get("Polymer", 0),
            errors="coerce"
        )
    }


# --------------------------------------------------
# Month Days
# --------------------------------------------------

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

    month_no = month_map[month_name]

    return calendar.monthrange(
        year,
        month_no
    )[1]


# --------------------------------------------------
# Water Volume
# --------------------------------------------------

def get_water_volume(
        production_mld,
        days
):

    return production_mld * days


# --------------------------------------------------
# ppm × ML = kg
# kg / 1000 = MT
# --------------------------------------------------

def chemical_mt_from_dose(
        dose_ppm,
        water_volume
):

    kg = dose_ppm * water_volume

    mt = kg / 1000

    return round(mt, 2)


# --------------------------------------------------
# Risk Buffer
# --------------------------------------------------

def apply_buffer(
        quantity_mt,
        scenario
):

    scenario = scenario.lower()

    if scenario == "normal":

        return round(
            quantity_mt * 1.10,
            2
        )

    elif scenario == "elevated":

        return round(
            quantity_mt * 1.20,
            2
        )

    elif scenario == "extreme":

        return round(
            quantity_mt * 1.30,
            2
        )

    return quantity_mt
