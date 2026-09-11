def calculate_days_remaining(
        current_stock,
        avg_daily_consumption
):

    if avg_daily_consumption == 0:
        return 0

    return round(
        current_stock /
        avg_daily_consumption,
        1
    )


def calculate_reorder_point(
        lead_time,
        avg_daily_consumption
):

    return (
        lead_time *
        avg_daily_consumption
    )


def calculate_safety_stock(
        avg_daily_consumption,
        safety_days=7
):

    return (
        avg_daily_consumption *
        safety_days
    )
