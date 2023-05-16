from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rss_reader.core.config import settings
from rss_reader.db.session import SessionLocal
from rss_reader.db.base_class import Base
from rss_reader.main import app
from rss_reader.main import get_db


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.TEST_SQLALCHEMY_DATABASE_URL)
    # if not database_exists:
    #     create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    Session = sessionmaker()
    db = Session(bind=connection)

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


# @pytest.fixture(scope="session")
# def db() -> Generator:
#     yield SessionLocal()
#
#
# @pytest.fixture(scope="module")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c



