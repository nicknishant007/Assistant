from  datetime import datetime,timedelta,timezone
from services.preference_service import (get_user_preferences)

from services.calendar_service import (build_calendar_service,get_day_events)

def find_free_slots(
    events: list,
    wake_time,
    sleep_time
):
    free_slots = []

    current_start = wake_time

    for event in events:

        start_str = (
            event["start"]
            .get("dateTime")
        )

        if not start_str:
            continue

        event_start = datetime.fromisoformat(
            start_str.replace("Z", "+00:00")
        ).time()

        event_end = datetime.fromisoformat(
            event["end"]["dateTime"]
            .replace("Z", "+00:00")
        ).time()

        if current_start < event_start:

            free_slots.append(
                (
                    current_start,
                    event_start
                )
            )

        current_start = max(
            current_start,
            event_end
        )

    if current_start < sleep_time:

        free_slots.append(
            (
                current_start,
                sleep_time
            )
        )

    return free_slots

def choose_best_slot(
    free_slots,
    duration_minutes: int
):
    required = timedelta(
        minutes=duration_minutes
    )

    for start, end in free_slots:

        start_dt = datetime.combine(
            datetime.today(),
            start
        )

        end_dt = datetime.combine(
            datetime.today(),
            end
        )

        if end_dt - start_dt >= required:

            return (
                start,
                (
                    start_dt + required
                ).time()
            )

    return None


def schedule_task(
    db,
    user_id: str,
    date,
    duration_minutes: int
):

    preferences = get_user_preferences(
        db,
        user_id
    )

    service = build_calendar_service(
        db,
        user_id
    )

    events = get_day_events(
        service,
        date
    )

    free_slots = find_free_slots(
        events,
        preferences.wake_time,
        preferences.sleep_time
    )

    return choose_best_slot(
        free_slots,
        duration_minutes
    )