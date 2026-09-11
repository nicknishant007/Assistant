from  datetime import datetime,timedelta,timezone
from services.preference_service import (get_user_preferences)

from services.calendar_service import (build_calendar_service,get_day_events,create_event,get_events_range
                                       ,update_event,delete_event)

#Helper

def to_iso(value):

    if isinstance(value, str):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    raise ValueError(
        f"Unsupported datetime type: {type(value)}"
    )


#helper find slot
def find_free_slots_from_events(
    events,
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
            start_str.replace(
                "Z",
                "+00:00"
            )
        ).time()

        event_end = datetime.fromisoformat(
            event["end"]["dateTime"]
            .replace(
                "Z",
                "+00:00"
            )
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
##find free slot
def find_free_slots(
    db,
    user_id: str,
    date
):
    if isinstance(date, str):
        date = datetime.fromisoformat(date).date()

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

    return find_free_slots_from_events(
        events=events,
        wake_time=preferences.wake_time,
        sleep_time=preferences.sleep_time
    )
#helper choose slot
def choose_best_slot_from_free_slots(
    free_slots,
    date,
    duration_minutes
):
    if isinstance(date, str):
        date = datetime.fromisoformat(date).date()

    required_duration = timedelta(
        minutes=duration_minutes
    )

    actual_date = (
        date.date()
        if isinstance(date, datetime)
        else date
    )

    for start_time, end_time in free_slots:

        start_dt = datetime.combine(
            actual_date,
            start_time
        )

        end_dt = datetime.combine(
            actual_date,
            end_time
        )

        if end_dt - start_dt >= required_duration:

            final_end_dt = (
                start_dt + required_duration
            )

            return {
                "start_time": start_time,
                "end_time": final_end_dt.time(),

                "start_datetime":
                    start_dt.isoformat(),

                "end_datetime":
                    final_end_dt.isoformat()
            }

    return None
##Choose best slot
def choose_best_slot(
    free_slots,
    date,
    duration_minutes: int
):  
    if isinstance(date, str):
        date = datetime.fromisoformat(date).date()

    return choose_best_slot_from_free_slots(
        free_slots=free_slots,
        date=date,
        duration_minutes=duration_minutes
    )

# SCHEDULE A EVENT (EVENT_TITLE, DATE, DURATION GIVE)


def schedule_task_fixed_time(
    db,
    user_id: str,
    title: str,
    start_datetime,
    duration_minutes: int
):

    if isinstance(start_datetime, str):
        start_datetime = datetime.fromisoformat(
            start_datetime
        )

    end_datetime = (
        start_datetime +
        timedelta(minutes=duration_minutes)
    )

    return create_event(
        db=db,
        user_id=user_id,
        title=title,
        start_time=to_iso(start_datetime),
        end_time=to_iso(end_datetime)
    )

##Schedule event(time not given)
def schedule_task_auto(
    db,
    user_id:str,
    title:str,
    start_datetime,
    end_datetime
):

    return create_event(
        db=db,
        user_id=user_id,
        title=title,
        start_time=to_iso(start_datetime),
        end_time=to_iso(end_datetime)
    )


#tomorrow full next day check we have also max day limit
def find_next_available_day(
    db,
    user_id: str,
    start_date,
    duration_minutes: int,
    max_days: int = 7
):

    preferences = get_user_preferences(
        db,
        user_id
    )

    service = build_calendar_service(
        db,
        user_id
    )

    events = get_events_range(
        service,
        start_date,
        start_date + timedelta(days=max_days)
    )

    for i in range(max_days):

        current_date = (
            start_date
            + timedelta(days=i)
        )

        day_events = []

        for event in events:

            start_str = (
                event["start"]
                .get("dateTime")
            )

            if not start_str:
                continue

            event_date = (
                datetime.fromisoformat(
                    start_str.replace(
                        "Z",
                        "+00:00"
                    )
                ).date()
            )

            if event_date == current_date.date():
                day_events.append(event)

        free_slots = (
            find_free_slots_from_events(
                events=day_events,
                wake_time=preferences.wake_time,
                sleep_time=preferences.sleep_time
            )
        )

        slot = (
            choose_best_slot_from_free_slots(
                free_slots=free_slots,
                date=current_date,
                duration_minutes=duration_minutes
            )
        )

        if slot:

            return {
                "date": current_date.date(),
                "slot": slot
            }

    return None

#Date and Time Normalizer
def normalize_datetimes(
    start_datetime=None,
    end_datetime=None,
    date=None,
    start_time=None,
    end_time=None
):
    if isinstance(date, str):
        date = datetime.fromisoformat(date).date()

    """
    Supports either:

    1.
    start_datetime + end_datetime

    OR

    2.
    date + start_time + end_time
    """

    if start_datetime and end_datetime:
        return (
            start_datetime,
            end_datetime
        )

    if date and start_time and end_time:

        start_datetime = (
            f"{date}T{start_time}"
        )

        end_datetime = (
            f"{date}T{end_time}"
        )

        return (
            start_datetime,
            end_datetime
        )

    raise ValueError(
        "Provide either "
        "(start_datetime,end_datetime) "
        "or "
        "(date,start_time,end_time)"
    )

#Reschedule Task
def reschedule_event(
    db,
    user_id: str,
    event_id: str,
    title: str,

    start_datetime=None,
    end_datetime=None,

    date=None,
    start_time=None,
    end_time=None
):
    if isinstance(date, str):
        date = datetime.fromisoformat(date).date()

    """
    Reschedule an existing event.

    Supported formats:

    1.
    start_datetime + end_datetime

    2.
    date + start_time + end_time
    """

    (
        start_datetime,
        end_datetime
    ) = normalize_datetimes(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    print("EVENT ID:", event_id)
    print("TITLE:", title)

    print("DATE:", date)
    print("START TIME:", start_time)
    print("END TIME:", end_time)

    print("START DATETIME:", start_datetime)
    print("END DATETIME:", end_datetime)

    return update_event(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=title,
        start_time=start_datetime,
        end_time=end_datetime
    )


# DELETE EVENT
def delete_task(
    db,
    user_id: str,
    event_id: str
):
    delete_event(
        db=db,
        user_id=user_id,
        event_id=event_id
    )

    return {
        "success": True,
        "message": "Event deleted successfully"
    }