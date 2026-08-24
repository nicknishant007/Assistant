from database.base import Base
from database.db import engine

import database.models


def init_db():

    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()