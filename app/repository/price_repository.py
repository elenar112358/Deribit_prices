import uuid

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

from datetime import date, datetime, time, timedelta, timezone

from app.models import Currency, IndexPrice
from app.schemas import PricesResponse, PricesLineResponse


def create_index_price(
    db: Session,
    currency_id: uuid.UUID,
    price: Decimal,
    timestamp: int,
) -> uuid.UUID:
    index_price = IndexPrice(
        currency_id=currency_id,
        price=price,
        timestamp=timestamp,
    )

    db.add(index_price)
    db.flush()

    return index_price.id


def get_prices(db: Session, currency: str) -> PricesLineResponse:
    query = (
        select(IndexPrice.price, IndexPrice.timestamp)
        .join(Currency, IndexPrice.currency_id == Currency.id)
        .where(Currency.ticker == currency)
        .order_by(IndexPrice.timestamp)
    )

    rows = db.execute(query).all()

    return PricesLineResponse(
        currency=currency,
        prices=[row.price for row in rows],
        timestamps=[row.timestamp for row in rows],
    )

def get_last_price(db: Session, currency: str) -> PricesResponse | None:
    query = (
        select(Currency.ticker, IndexPrice.price, IndexPrice.timestamp)
        .join(Currency, IndexPrice.currency_id == Currency.id)
        .where(Currency.ticker == currency)
        .order_by(IndexPrice.timestamp.desc(), IndexPrice.id.desc())
        .limit(1)
    )

    row = db.execute(query).first()

    if row is None:
        return None

    return PricesResponse(
        currency=row.ticker,
        price=row.price,
        timestamp=row.timestamp,
    )

def get_date_prices(db: Session, target_date: date, currency: str) -> list[PricesResponse]:
    start = datetime.combine(
        target_date,
        time.min,
        tzinfo=timezone.utc,
    )
    end = start + timedelta(days=1)

    start_timestamp = int(start.timestamp())
    end_timestamp = int(end.timestamp())

    query = (
        select(Currency.ticker, IndexPrice.price, IndexPrice.timestamp)
        .join(Currency, IndexPrice.currency_id == Currency.id)
        .where(
            Currency.ticker == currency,
            IndexPrice.timestamp >= start_timestamp,
            IndexPrice.timestamp < end_timestamp,
        )
        .order_by(IndexPrice.timestamp)
    )

    rows = db.execute(query).all()

    return [
        PricesResponse(
            currency=row.ticker,
            price=row.price,
            timestamp=row.timestamp,
        )
        for row in rows
    ]