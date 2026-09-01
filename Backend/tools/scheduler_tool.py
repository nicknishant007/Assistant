from services.scheduler_service import (
    schedule_task,reschedule_task,find_free_slots,
    delete_task,find_next_available_day)


def schedule_task_tool(
    db,
    user_id,
    title,
    date,
    duration_minutes
):
    return schedule_task(
        db=db,
        user_id=user_id,
        title=title,
        date=date,
        duration_minutes=duration_minutes
    )


def reschedule_task_tool(
    db,
    user_id,
    event_name,
    start_date,
    duration_minutes
):
    return reschedule_task(
        db=db,
        user_id=user_id,
        event_name=event_name,
        start_date=start_date,
        duration_minutes=duration_minutes
    )


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

def delete_task_tool(
    db,
    user_id: str,
    title: str
):
    return delete_task(
        db=db,
        user_id=user_id,
        title=title
    )

def next_available_day_tool(
    db,
    user_id: str,
    start_date,
    duration_minutes: int,
    max_days: int = 7
):
    return find_next_available_day(
        db=db,
        user_id=user_id,
        start_date=start_date,
        duration_minutes=duration_minutes,
        max_days=max_days
    )