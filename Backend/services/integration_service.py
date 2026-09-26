from datetime import datetime
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


def get_notion_integration(
    db: Session,
    user_id: str
):
    return get_integration(
        db=db,
        user_id=user_id,
        provider="notion"
    )


def create_or_update_integration(
    db: Session,
    user_id: str,
    provider: str,
    access_token: str,
    refresh_token: str | None,
    client_id: str | None = None,
    expires_at: datetime | None = None
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

        if client_id is not None:
            integration.notion_client_id = client_id

        if expires_at is not None:
            integration.token_expires_at = expires_at

        integration.connected = True

    else:
        integration = UserIntegration(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            notion_client_id=client_id,
            token_expires_at=expires_at,
            connected=True
        )

        db.add(integration)

    db.commit()
    db.refresh(integration)

    return integration


def disconnect_integration(
    db: Session,
    user_id: str,
    provider: str
):
    integration = get_integration(
        db=db,
        user_id=user_id,
        provider=provider
    )

    if not integration:
        return None

    integration.connected = False
    integration.access_token = None
    integration.refresh_token = None

    db.commit()
    db.refresh(integration)

    return integration