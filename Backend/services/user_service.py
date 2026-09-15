from sqlalchemy.orm import Session
from database.models.user import User

import uuid
from datetime import datetime


def get_user_by_email(
    db: Session,
    email: str
):

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    email: str,
    full_name: str,
    profile_picture: str
):

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name=full_name,
        profile_picture=profile_picture,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def update_user(
    db: Session,
    user: User,
    full_name: str | None = None,
    profile_picture: str | None = None
):
    """Partial update of the authenticated user's own profile."""

    if full_name is not None:
        user.full_name = full_name

    if profile_picture is not None:
        user.profile_picture = profile_picture

    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return user