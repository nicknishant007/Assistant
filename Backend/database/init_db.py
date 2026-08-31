from database.base import Base
from database.db import engine

from database.models.user import User
from Backend.database.models.user_integration import UserIntegration
from database.models.user_preference import UserPreference


def init_db():

    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()