import pandas as pd


DATA_PATH = "data"


def load_daily_turbidity():
    df = pd.read_excel(
        f"{DATA_PATH}/Daily Turbidity Data_Pc.xlsx"
    )

    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

    return df


def load_monthly_turbidity():
    df = pd.read_excel(
        f"{DATA_PATH}/Monthly Historical Turbidity_Pc.xlsx"
    )

    df.columns = df.columns.str.strip()

    return df


def load_chemical_consumption():
    df = pd.read_excel(
        f"{DATA_PATH}/Chemical_consumption_data_Pc.xlsx"
    )

    df.columns = df.columns.str.strip()

    return df


def load_current_scc():
    df = pd.read_excel(
        f"{DATA_PATH}/Current_SCC_Pc.xlsx"
    )

    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

    return df


def load_lrd():
    df = pd.read_excel(
        f"{DATA_PATH}/LRD_Pc.xlsx"
    )

    df.columns = df.columns.str.strip()

    return df

