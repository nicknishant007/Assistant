import uuid

from datetime import datetime
from sqlalchemy import (String,DateTime,ForeignKey,Text)
from sqlalchemy.orm import (Mapped,mapped_column)

from database.base import Base


class ConversationMessage(Base):

    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    conversation_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "agent_conversations.id"
        ),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )