from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from dependencies.auth import get_current_user
from database.models.user import User
from schemas.preference import PreferencesResponse, PreferencesUpdateRequest
from services.preference_service import (
    get_or_create_user_preferences,
    update_user_preferences
)

router = APIRouter(
    prefix="/api/preferences",
    tags=["Preferences"]
)


@router.get("", response_model=PreferencesResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_or_create_user_preferences(db, current_user.id)


@router.put("", response_model=PreferencesResponse)
def update_preferences(
    data: PreferencesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_user_preferences(
        db=db,
        user_id=current_user.id,
        wake_time=data.wake_time,
        sleep_time=data.sleep_time,
        work_start_time=data.work_start_time,
        focus_duration=data.focus_duration
    )