import uuid

from datetime import datetime
from sqlalchemy import (String,DateTime,ForeignKey,JSON)
from sqlalchemy.orm import (Mapped,mapped_column)

from database.base import Base


class AgentConversation(Base):

    __tablename__ = "agent_conversations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String,
        default="active"
    )

    state: Mapped[dict] = mapped_column(
        JSON,
        default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    conversation_title: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )