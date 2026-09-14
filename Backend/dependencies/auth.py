from fastapi import Cookie,Depends
from database.session import get_db
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.session import SessionLocal
from database.models.user import User
from utils.security import verify_token

def get_current_user(access_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(401, "Not authenticated")
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user

