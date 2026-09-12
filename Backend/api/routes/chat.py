from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.chat import (ChatRequest,ChatResponse)
from services.chat_service import chat_service
from dependencies.auth import get_current_user
from database.models.user import User
from Backend.agent.state import AgentState
from Backend.agent.graph import graph

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

def chat_service(
    db,
    user_id: str,
    conversation_id: str,
    message: str
):

    state = AgentState(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
        user_query=message
    )

    result = graph.invoke(state)

    return {
        "response": result.final_response
    }