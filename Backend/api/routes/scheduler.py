from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db
from datetime import datetime 
from schemas.scheduler import ScheduleTaskRequest
from services.calendar_service import create_event
from services.scheduler import schedule_task


from dependencies.auth import get_current_user
from services.preference_service import (get_user_preferences)

router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"]
)


@router.get("/preferences")
def get_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    preferences = get_user_preferences(
        db,
        current_user.id
    )

    return preferences


#
@router.get("/find-slot")
def find_slot(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    slot = schedule_task(
        db=db,
        user_id=current_user.id,
        date=datetime.now(),
        duration_minutes=120
    )

    return {
        "slot": slot
    }

#post task 

@router.post("/task")
def schedule_new_task(
    request: ScheduleTaskRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    slot = schedule_task(
        db=db,
        user_id=current_user.id,
        date=request.date,
        duration_minutes=request.duration_minutes
    )

    if not slot:
        return {
            "message": "No free slot found"
        }

    start_time, end_time = slot

    start_datetime = datetime.combine(
        request.date.date(),
        start_time
    )

    end_datetime = datetime.combine(
        request.date.date(),
        end_time
    )

    event = create_event(
        db=db,
        user_id=current_user.id,
        title=request.title,
        start_time=start_datetime.isoformat(),
        end_time=end_datetime.isoformat()
    )

    return event