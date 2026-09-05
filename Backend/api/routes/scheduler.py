from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database.session import get_db
from datetime import datetime

from schemas.scheduler import (
    ScheduleTaskRequest,
    RescheduleTaskRequest
)

from services.scheduler_service import (
    schedule_task,
    reschedule_task,
    find_free_slots,
    find_next_available_day
)

from dependencies.auth import get_current_user

from services.preference_service import (
    get_user_preferences
)

router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"]
)


@router.get("/preferences")
def get_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_user_preferences(
        db,
        current_user.id
    )


# FREE SLOTS
@router.get("/free-slots")
def get_free_slots(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    slots = find_free_slots(
        db=db,
        user_id=current_user.id,
        date=datetime.now()
    )

    return {
        "free_slots": slots
    }


# NEXT AVAILABLE DAY
@router.get("/next-available")
def next_available_day(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    result = find_next_available_day(
        db=db,
        user_id=current_user.id,
        start_date=datetime.now(),
        duration_minutes=120
    )

    return result


# SCHEDULE TASK
@router.post("/task")
def schedule_new_task(
    request: ScheduleTaskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    event = schedule_task(
        db=db,
        user_id=current_user.id,
        title=request.title,
        date=request.date,
        duration_minutes=request.duration_minutes
    )

    if not event:
        return {
            "message": "No free slot found"
        }

    return event


# RESCHEDULE TASK
@router.post("/reschedule")
def reschedule_existing_task(
    request: RescheduleTaskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    event = reschedule_task(
        db=db,
        user_id=current_user.id,
        event_name=request.event_name,
        start_date=request.start_date,
        duration_minutes=request.duration_minutes
    )

    if not event:
        return {
            "message": "No available slot found"
        }

    return event