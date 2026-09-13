from sqlalchemy.orm import Session

from schemas.chat import ChatResponse

from agent.state import AgentState
from agent.graph import graph

from services.conversation_service import (
    create_conversation,
    get_conversation,
    add_message,
    get_recent_messages
)


def chat_service(
    db: Session,
    user_id: str,
    message: str,
    conversation_id: str | None = None
):

    # ==========================================
    # Resolve Conversation
    # ==========================================

    if conversation_id:

        conversation = get_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:

            conversation = create_conversation(
                db=db,
                user_id=user_id,
                title=message[:50]
            )

            conversation_id = conversation.id

    else:

        conversation = create_conversation(
            db=db,
            user_id=user_id,
            title=message[:50]
        )

        conversation_id = conversation.id

    # ==========================================
    # Load Conversation History
    # ==========================================

    messages = get_recent_messages(
        db=db,
        conversation_id=conversation_id,
        limit=50
    )

    # ==========================================
    # Save User Message
    # ==========================================

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message
    )

    # ==========================================
    # Build Agent State
    # ==========================================

    state = AgentState(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
        user_query=message,
        conversation_history=[
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    )

    # ==========================================
    # Run Graph
    # ==========================================

    result = graph.invoke(state)

    # ==========================================
    # Handle LangGraph Result
    # ==========================================

    if isinstance(result, dict):

        assistant_message = (
            result.get("final_response")
            or result.get("pending_question")
            or result.get("approval_message")
            or result.get("error")
            or "Unable to process request."
        )

    else:

        assistant_message = (
            result.final_response
            or result.pending_question
            or result.approval_message
            or result.error
            or "Unable to process request."
        )

    # ==========================================
    # Save Assistant Message
    # ==========================================

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_message
    )

    # ==========================================
    # Return
    # ==========================================

    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_message
    )