import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from furniture.orm import mapper_registry, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    mapper_registry.metadata.create_all(in_memory_db)
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()