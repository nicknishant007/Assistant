from fastapi import Cookie
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.session import SessionLocal
from database.models.user import User
from utils.security import verify_token

def get_current_user(
    access_token: str | None = Cookie(
        default=None)):
    print("COOKIE=",access_token)

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated")
    
    payload=verify_token(access_token)
    print("PAYLOAD=",payload)
    user_id=payload.get("sub")
    db=SessionLocal()
    user=(db.query(User).filter(User.id==user_id).first())
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found")
    return user

