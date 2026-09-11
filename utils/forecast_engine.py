import pandas as pd

from utils.data_loader import load_lrd


def get_recommended_dose(
        current_turbidity
):

    lrd_df = load_lrd()

    lrd_df["difference"] = abs(
        lrd_df["Raw_Turbidity_NTU"]
        - current_turbidity
    )

    row = lrd_df.sort_values(
        "difference"
    ).iloc[0]

    return {
        "Raw Turbidity": row["Raw_Turbidity_NTU"],
        "S/Alum": row["S/Alum"],
        "L/Alum": row["L/Alum"],
        "P/PAC": row["P/PAC"],
        "L/PAC": row["L/PAC"],
        "Polymer": row["Polymer"]
    }
`

