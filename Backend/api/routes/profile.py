from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from dependencies.auth import get_current_user
from database.models.user import User
from schemas.user import UserProfileResponse, UserProfileUpdateRequest
from services.user_service import update_user

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)


@router.get("", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_user(
        db=db,
        user=current_user,
        full_name=data.full_name,
        profile_picture=data.profile_picture
    )