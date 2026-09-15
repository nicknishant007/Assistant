from sqlalchemy.orm import Session
from database.models.user_preference import UserPreference


def get_user_preferences(
        db: Session,
        user_id: str):
    return (
        db.query(UserPreference).filter(
            UserPreference.user_id == user_id).first()
        )


def get_or_create_user_preferences(
    db: Session,
    user_id: str
):
    """
    Preference rows aren't created at signup today, so a brand-new
    user has none. Rather than 404ing the preferences page, create a
    default row on first read.
    """

    preferences = get_user_preferences(db, user_id)

    if not preferences:

        preferences = UserPreference(
            user_id=user_id
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


def update_user_preferences(
    db: Session,
    user_id: str,
    wake_time=None,
    sleep_time=None,
    work_start_time=None,
    focus_duration=None
):
    preferences = get_or_create_user_preferences(db, user_id)

    if wake_time is not None:
        preferences.wake_time = wake_time

    if sleep_time is not None:
        preferences.sleep_time = sleep_time

    if work_start_time is not None:
        preferences.work_start_time = work_start_time

    if focus_duration is not None:
        preferences.focus_duration = focus_duration

    db.commit()
    db.refresh(preferences)

    return preferences