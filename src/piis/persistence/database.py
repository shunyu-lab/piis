from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from piis.persistence.models import Base


def create_runtime_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return engine


def create_session_factory(database_url: str) -> sessionmaker:
    engine = create_runtime_engine(database_url)
    return sessionmaker(engine, expire_on_commit=False)
