from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from dependencies.auth import get_current_user
from database.models.user import User
from services.conversation_service import (
    get_user_conversations,
    get_conversation,
    get_messages,
    delete_conversation
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = get_user_conversations(db, current_user.id)
    return [
        {
            "id": c.id,
            "title": c.conversation_title or "New Conversation",
            "updatedAt": c.updated_at.isoformat()
        }
        for c in conversations
    ]


@router.get("/{conversation_id}")
def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    messages = get_messages(db, conversation_id)
    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.conversation_title or "New Conversation",
            "updatedAt": conversation.updated_at.isoformat()
        },
        "messages": [
            {
                "id": m.id,
                "conversationId": m.conversation_id,
                "role": m.role,
                "content": m.content,
                "createdAt": m.created_at.isoformat()
            }
            for m in messages
        ]
    }


@router.delete("/{conversation_id}")
def remove_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    delete_conversation(db, conversation_id)
    return {"success": True}