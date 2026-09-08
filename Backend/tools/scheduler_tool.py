from services.scheduler_service import (
    schedule_task_fixed_time,
    schedule_task_auto,

    reschedule_task_fixed,
    reschedule_task_day,
    reschedule_task_next_available,

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
    return find_free_slots(
        db=db,
        user_id=user_id,
        date=date
    )


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


# RESCHEDULE FIXED

def reschedule_task_fixed_tool(
    db,
    user_id,
    event_id,
    title,
    start_datetime,
    end_datetime
):
    return reschedule_task_fixed(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )


# RESCHEDULE DAY

def reschedule_task_day_tool(
    db,
    user_id,
    event_id,
    title,
    start_datetime,
    end_datetime
):
    return reschedule_task_day(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )


# RESCHEDULE NEXT AVAILABLE

def reschedule_task_next_available_tool(
    db,
    user_id,
    event_id,
    title,
    start_datetime,
    end_datetime
):
    return reschedule_task_next_available(
        db=db,
        user_id=user_id,
        event_id=event_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime
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