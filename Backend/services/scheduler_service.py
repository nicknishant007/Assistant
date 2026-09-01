from  datetime import datetime,timedelta,timezone
from services.preference_service import (get_user_preferences)

from services.calendar_service import (build_calendar_service,get_day_events,create_event,get_events_range
                                       ,find_event_by_title,update_event,
                                       delete_event)

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

    required_duration = timedelta(
        minutes=duration_minutes
    )

    for start_time, end_time in free_slots:

        start_dt = datetime.combine(
            date.date(),
            start_time
        )

        end_dt = datetime.combine(
            date.date(),
            end_time
        )

        if (
            end_dt - start_dt
            >= required_duration
        ):

            return (
                start_time,
                (
                    start_dt
                    + required_duration
                ).time()
            )

    return None
##Choose best slot
def choose_best_slot(
    db,
    user_id: str,
    date,
    duration_minutes: int
):

    free_slots = find_free_slots(
        db=db,
        user_id=user_id,
        date=date
    )

    return choose_best_slot_from_free_slots(
        free_slots=free_slots,
        date=date,
        duration_minutes=duration_minutes
    )

##Schedule event
def schedule_task(
    db,
    user_id: str,
    title: str,
    date,
    duration_minutes: int
):

    slot = choose_best_slot(
        db=db,
        user_id=user_id,
        date=date,
        duration_minutes=duration_minutes
    )

    if not slot:
        return None

    start_time, end_time = slot

    start_datetime = datetime.combine(
        date.date(),
        start_time
    )

    end_datetime = datetime.combine(
        date.date(),
        end_time
    )

    created_event = create_event(
        db=db,
        user_id=user_id,
        title=title,
        start_time=start_datetime.isoformat(),
        end_time=end_datetime.isoformat()
    )

    return created_event


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

##Reschedule Task
def reschedule_task(
    db,
    user_id: str,
    event_name: str,
    start_date,
    duration_minutes: int
):

    matching_events = find_event_by_title(
        db=db,
        user_id=user_id,
        title=event_name
    )

    if not matching_events:
        raise Exception(
            "Event not found"
        )

    event = matching_events[0]

    event_id = event["id"]

    slot_data = find_next_available_day(
        db=db,
        user_id=user_id,
        start_date=start_date,
        duration_minutes=duration_minutes
    )

    if not slot_data:
        return None

    slot_start, slot_end = (
        slot_data["slot"]
    )

    event_date = (
        slot_data["date"]
    )

    start_datetime = datetime.combine(
        event_date,
        slot_start
    )

    end_datetime = datetime.combine(
        event_date,
        slot_end
    )

    updated_event = update_event(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=event["summary"],
        start_time=start_datetime.isoformat(),
        end_time=end_datetime.isoformat()
    )

    return updated_event

# DELETE EVENT
def delete_task(
    db,
    user_id: str,
    title: str
):

    matching_events = find_event_by_title(
        db=db,
        user_id=user_id,
        title=title
    )

    if not matching_events:
        return {
            "success": False,
            "message": f"No event found with title '{title}'"
        }

    event = matching_events[0]

    delete_event(
        db=db,
        user_id=user_id,
        event_id=event["id"]
    )

    return {
        "success": True,
        "message": f"Event '{title}' deleted successfully"
    }