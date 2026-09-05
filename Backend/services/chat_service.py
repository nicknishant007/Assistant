from sqlalchemy.orm import Session

from schemas.chat import ChatResponse

from services.conversation_service import (
    create_conversation,
    add_message,
    get_messages
)

from agent.planner_agent import planner_agent


def chat_service(
    db: Session,
    user_id: str,
    message: str,
    conversation_id: str | None = None
):

    # Create conversation if needed
    if not conversation_id:

        conversation = create_conversation(
            db=db,
            user_id=user_id,
            title=message[:50]
        )

        conversation_id = conversation.id

    # Store user message
    add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message
    )

    # Fetch history
    messages = get_messages(
        db=db,
        conversation_id=conversation_id
    )

    # Planner
    planner_result = planner_agent(
        messages
    )

    assistant_message = (
        planner_result["message"]
    )

    # Store assistant response
    add_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_message
    )

    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_message
    )