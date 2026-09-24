from fastapi import Cookie,Depends
from database.session import get_db
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.session import SessionLocal
from database.models.user import User
from utils.security import verify_token


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    print("COOKIE RECEIVED:", access_token)

    if not access_token:
        print("NO COOKIE FOUND")
        raise HTTPException(401, "Not authenticated")

    payload = verify_token(access_token)

    print("PAYLOAD:", payload)

    if not payload:
        print("TOKEN INVALID")
        raise HTTPException(401, "Invalid or expired token")

    user = db.query(User).filter(
        User.id == payload.get("sub")
    ).first()

    print("USER:", user)

    if not user:
        raise HTTPException(401, "User not found")

    return user