from sqlalchemy.orm import Session

from schemas.chat import ChatResponse

from agent.state import AgentState
from agent.planner_agent import planner_agent

from services.conversation_service import (
    create_conversation,
    add_message,
    get_recent_messages
)


def chat_service(
    db: Session,
    user_id: str,
    message: str,
    conversation_id: str | None = None
):

    # --------------------------------------------------
    # Create Conversation
    # --------------------------------------------------

    if not conversation_id:

        conversation = create_conversation(
            db=db,
            user_id=user_id,
            title=message[:50]
        )

        conversation_id = conversation.id

    # --------------------------------------------------
    # Save User Message
    # --------------------------------------------------

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message
    )

    # --------------------------------------------------
    # Fetch Last Messages
    # --------------------------------------------------

    messages = get_recent_messages(
        db=db,
        conversation_id=conversation_id,
        limit=50
    )

    # --------------------------------------------------
    # Build Agent State
    # --------------------------------------------------

    state = AgentState(
        user_id=user_id,
        conversation_id=conversation_id,
        user_query=message
    )

    state.conversation_history = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in messages
    ]

    # --------------------------------------------------
    # Planner
    # --------------------------------------------------

    state = planner_agent(
        state=state
    )

    # --------------------------------------------------
    # Extract Response
    # --------------------------------------------------

    if state.next_step == "ask_user":

        assistant_message = (
            state.pending_question
        )

    elif state.next_step == "approval":

        assistant_message = (
            state.approval_message
        )

    elif state.final_response:

        assistant_message = (
            state.final_response
        )

    else:

        assistant_message = (
            "Unable to process request."
        )

    # --------------------------------------------------
    # Save Assistant Message
    # --------------------------------------------------

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_message
    )

    # --------------------------------------------------
    # Return Response
    # --------------------------------------------------

    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_message
    )