from services.scheduler_service import (
    schedule_task_fixed_time,
    schedule_task_auto,

    reschedule_event,

    find_free_slots,
    choose_best_slot,
    delete_task,
    find_next_available_day
)

# SCHEDULE AT EXACT TIME

def schedule_task_fixed_tool(
    db,
    user_id,
    title,
    start_datetime,
    duration_minutes
):
    return schedule_task_fixed_time(
        db=db,
        user_id=user_id,
        title=title,
        start_datetime=start_datetime,
        duration_minutes=duration_minutes
    )


# AUTO SCHEDULE

def schedule_task_auto_tool(
    db,
    user_id,
    title,
    start_datetime,
    end_datetime
):
    return schedule_task_auto(
        db=db,
        user_id=user_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )


# FIND FREE SLOTS

def free_slots_tool(
    db,
    user_id,
    date
):
    slots=find_free_slots(
        db=db,
        user_id=user_id,
        date=date
    )
    return {
        "free_slots":slots
    }


# CHOOSE BEST SLOT

def choose_best_slot_tool(
    free_slots,
    date,
    duration_minutes,
    **kwargs
):
    return choose_best_slot(
        free_slots=free_slots,
        date=date,
        duration_minutes=duration_minutes
    )

# FIND NEXT AVAILABLE DAY

def next_available_day_tool(
    db,
    user_id,
    start_date,
    duration_minutes,
    max_days=7
):
    return find_next_available_day(
        db=db,
        user_id=user_id,
        start_date=start_date,
        duration_minutes=duration_minutes,
        max_days=max_days
    )


# RESCHEDULE EVENT


def reschedule_event_tool(
    db,
    user_id,
    event_id,
    title,

    start_datetime=None,
    end_datetime=None,

    date=None,
    start_time=None,
    end_time=None
):
    return reschedule_event(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=title,

        start_datetime=start_datetime,
        end_datetime=end_datetime,

        date=date,
        start_time=start_time,
        end_time=end_time
    )


# DELETE EVENT

def delete_task_tool(
    db,
    user_id,
    event_id
):
    return delete_task(
        db=db,
        user_id=user_id,
        event_id=event_id
    )