import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import session, sessionmaker, clear_mappers
from app.orm import metadata, start_mappers


@pytest.fixture()
def session():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(engine)()
    clear_mappers()
    metadata.drop_all(engine)
    engine.dispose()
