from sqlalchemy.orm import Session

from database.models.user_integration import UserIntegration


def get_integration(
    db: Session,
    user_id: str,
    provider: str
):
    return (
        db.query(UserIntegration)
        .filter(
            UserIntegration.user_id == user_id,
            UserIntegration.provider == provider
        )
        .first()
    )


def get_google_integration(
    db: Session,
    user_id: str
):
    return get_integration(
        db=db,
        user_id=user_id,
        provider="google_calendar"
    )


def create_or_update_integration(
    db: Session,
    user_id: str,
    provider: str,
    access_token: str,
    refresh_token: str | None
):
    integration = get_integration(
        db=db,
        user_id=user_id,
        provider=provider
    )

    if integration:

        integration.access_token = access_token

        if refresh_token:
            integration.refresh_token = refresh_token

        integration.connected = True

    else:

        integration = UserIntegration(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            connected=True
        )

        db.add(integration)

    db.commit()
    db.refresh(integration)

    return integration