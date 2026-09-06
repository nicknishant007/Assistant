from database.models.agent_conversation import AgentConversation
from database.models.conversation_message import ConversationMessage


def create_conversation(
    db,
    user_id: str,
    title: str = "New Conversation"
):

    conversation = AgentConversation(
        user_id=user_id,
        conversation_title=title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db,
    conversation_id: str
):

    return (
        db.query(AgentConversation)
        .filter(
            AgentConversation.id == conversation_id
        )
        .first()
    )


def add_message(
    db,
    conversation_id: str,
    role: str,
    content: str
):

    message = ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()

    return message


def get_recent_messages(
    db,
    conversation_id: str,
    limit: int = 55
):

    messages=(
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id== conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()
    return messages

def get_messages(
        db,
        converstion_id: str
):
    messages=(db.query(ConversationMessage)
              .filter(ConversationMessage.conversation_id==converstion_id)
              .order_by(ConversationMessage.created_at.asc()).all())
    return messages