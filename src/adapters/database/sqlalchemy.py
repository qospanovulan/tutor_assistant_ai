from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from adapters.database.mappings import start_mappers


def make_session_factory(database_url: str):
    engine = create_engine(database_url, future=True)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    start_mappers()

    return scoped_session(session_factory)
