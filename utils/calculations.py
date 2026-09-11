import numpy as np


def turbidity_statistics(series):

    return {
        "Mean": round(series.mean(), 2),
        "Median": round(series.median(), 2),
        "Max": round(series.max(), 2),
        "Min": round(series.min(), 2),
        "P50": round(np.percentile(series.dropna(), 50), 2),
        "P75": round(np.percentile(series.dropna(), 75), 2),
        "P90": round(np.percentile(series.dropna(), 90), 2),
        "P95": round(np.percentile(series.dropna(), 95), 2)
    }


def chemical_per_mld(
    chemical_consumption,
    production
):

    if production == 0:
        return 0

    return round(
        chemical_consumption / production,
        2
    )


def turbidity_risk(turbidity):

    if turbidity < 20:
        return "LOW"

    elif turbidity < 75:
        return "MODERATE"

    else:
        return "HIGH"
