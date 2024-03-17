import pytest
from pathlib import Path
import time
import requests
from requests.exceptions import ConnectionError

from sqlalchemy import create_engine, text
from sqlalchemy.orm import session, sessionmaker, clear_mappers
from sqlalchemy.exc import OperationalError
from app.orm import metadata, start_mappers
from app.config import get_postgres_url, get_api_url


@pytest.fixture()
def session():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(engine)()
    clear_mappers()
    metadata.drop_all(engine)
    engine.dispose()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(get_postgres_url())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture()
def add_stock(postgres_session):
    batches_added = set()
    sku_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            postgres_session.execute(
                text('INSERT INTO batches (ref, sku, _purchased_quantity, eta)'
                     ' VALUES (:ref, :sku, :qty, :eta)'),
                dict(ref=ref, sku=sku, qty=qty, eta=eta)
            )
            [[batch_id]] = postgres_session.execute(
                text('SELECT id FROM batches WHERE ref=:ref AND sku=:sku'),
                dict(ref=ref, sku=sku)
            )
            batches_added.add(batch_id)
            sku_added.add(sku)
        postgres_session.commit()

    yield _add_stock


@pytest.fixture
def restart_api():
    (Path(__file__).parents[1] / 'app/flask_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
