from sqlalchemy.orm import Session
from database.models.user_preference import UserPreference

def get_user_preferences(
        db:Session,
        user_id:str):
    return (
        db.query(UserPreference).filter(
            UserPreference.user_id==user_id).first()
        )
    
