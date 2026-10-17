from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database import Base
from app.dependency import get_db
from app.main import app

from decimal import Decimal

from app.models import Currency, IndexPrice

TEST_DATABASE_URL = (
    "postgresql+psycopg://test_user:test_password@test_db:5432/ss_test_db"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


def get_test_db() -> Generator[Session, None, None]:
    with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_get_db():
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    with TestSessionLocal() as session:
        yield session


@pytest.fixture
def saved_prices(db_session):
    currency = Currency(ticker="btc_usd")
    db_session.add(currency)
    db_session.flush()

    db_session.add_all([
        IndexPrice(
            currency_id=currency.id,
            price=Decimal("65000.25"),
            timestamp=1_800_000_001,
        ),
        IndexPrice(
            currency_id=currency.id,
            price=Decimal("65100.50"),
            timestamp=1_800_000_002,
        ),
    ])

    db_session.commit()
