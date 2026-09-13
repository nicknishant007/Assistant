from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.chat import (ChatRequest,ChatResponse)
from services.chat_service import chat_service
from dependencies.auth import get_current_user
from database.models.user import User

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    print("Current_User:",current_user.email)
    return chat_service(
        db=db,
        user_id=current_user.id,
        conversation_id=data.conversation_id,
        message=data.message
    )
