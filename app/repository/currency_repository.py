import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Currency


def currency_exists(db: Session, ticker: str) -> bool:
    item = select(Currency.id).where(Currency.ticker == ticker)

    return db.scalar(item) is not None


def get_currency_id(db: Session, ticker: str) -> uuid.UUID | None:
    item = select(Currency.id).where(Currency.ticker == ticker)

    return db.scalar(item)


def create_currency(db: Session, ticker: str) -> uuid.UUID:
    currency = Currency(ticker=ticker)
    db.add(currency)
    db.flush()

    return currency.id
