import uuid
from sqlalchemy import (String,Boolean,Text,ForeignKey)
from sqlalchemy.orm import (Mapped,mapped_column)

from database.base import Base

class UserIntegration(Base):

    __tablename__ = "user_integrations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    provider: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    connected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )