from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from config.settings import settings

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token:str):
    try:
        payload=jwt.decode(token,
                           settings.JWT_SECRET_KEY,
                           algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None