import uuid
from datetime import time
from sqlalchemy import (String,Integer,Time,ForeignKey)
from sqlalchemy.orm import (Mapped,mapped_column)

from database.base import Base


class UserPreference(Base):

    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )

    wake_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    sleep_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    work_start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    focus_duration: Mapped[int] = mapped_column(
        Integer,
        default=60
    )