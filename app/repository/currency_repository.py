import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Currency


# def currency_exists(db: Session, ticker: str) -> bool:
#     item = select(Currency.id).where(Currency.ticker == ticker)
#
#     return db.scalar(item) is not None


def get_currency_id(db: Session, ticker: str) -> uuid.UUID | None:
    item = select(Currency.id).where(Currency.ticker == ticker)

    return db.scalar(item)


def create_currency(db: Session, ticker: str) -> uuid.UUID:
    currency = Currency(ticker=ticker)
    db.add(currency)
    db.flush()

    return currency.id


# currency_id = get_currency_id(db, "btc_usd")
#
# if currency_id is None:
#     currency_id = create_currency(db, "btc_usd")
#
# price_id = create_index_price(
#     db=db,
#     currency_id=currency_id,
#     price=Decimal("67500.125"),
#     timestamp=1792087200,
# )
#
# db.commit()