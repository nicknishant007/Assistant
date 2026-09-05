from datetime import datetime, timedelta
import calendar


def resolve_day_name(day_name: str) -> str:
    """
    Monday -> 2026-09-07
    If day already passed this week,
    return next week's occurrence.
    """

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    today = datetime.now()

    target_day = weekdays[day_name.lower()]

    days_ahead = target_day - today.weekday()

    if days_ahead < 0:
        days_ahead += 7

    target_date = today + timedelta(days=days_ahead)

    return target_date.date().isoformat()


def resolve_day_of_month(day: int) -> str:
    """
    23 -> current month's 23rd
    If already passed, use next month.
    """

    today = datetime.now()

    year = today.year
    month = today.month

    if day < today.day:

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    max_day = calendar.monthrange(year, month)[1]

    if day > max_day:
        raise ValueError(
            f"Invalid day {day} for month {month}"
        )

    return f"{year}-{month:02d}-{day:02d}"