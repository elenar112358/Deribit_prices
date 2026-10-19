from datetime import date
from decimal import Decimal

from app.models import IndexPrice

from app.repository import price_repository

from uuid import UUID

from app.schemas import PricesLineResponse, PricesResponse


def test_create_index_price(db_session, saved_prices):
    currency_id = saved_prices["currency_id"]

    index_price_id = price_repository.create_index_price(
        db_session,
        currency_id=currency_id,
        price="5678.90",
        timestamp=1_800_000_003,
    )

    assert isinstance(index_price_id, UUID)

    index_price = db_session.get(IndexPrice, index_price_id)

    assert index_price is not None
    assert index_price.currency_id == currency_id
    assert index_price.price == Decimal("5678.90")
    assert index_price.timestamp == 1_800_000_003


def test_get_prices(db_session, saved_prices):
    prices = price_repository.get_prices(db_session, currency="btc_usd")

    assert isinstance(prices, PricesLineResponse)
    assert prices.currency == "btc_usd"
    assert prices.prices == [Decimal("65000.25"), Decimal("65100.50")]
    assert prices.timestamps == [1_800_000_001, 1_800_000_002]


def test_get_last_price(db_session, saved_prices):
    price = price_repository.get_last_price(db_session, currency="btc_usd")

    assert isinstance(price, PricesResponse)
    assert price.currency == "btc_usd"
    assert price.price == Decimal("65100.50")
    assert price.timestamp == 1_800_000_002

    price = price_repository.get_last_price(db_session, currency="unknown_currency")

    assert price is None


def test_get_date_prices(db_session, saved_prices):
    prices = price_repository.get_date_prices(db_session, target_date=date.fromisoformat("2027-01-15"),
                                              currency="btc_usd")

    assert isinstance(prices, list)
    for price in prices:
        assert isinstance(price, PricesResponse)

    assert len(prices) == 2

    assert prices[0].currency == "btc_usd"
    assert prices[0].price == Decimal("65000.25")
    assert prices[0].timestamp == 1_800_000_001

    assert prices[1].currency == "btc_usd"
    assert prices[1].price == Decimal("65100.50")
    assert prices[1].timestamp == 1_800_000_002

    prices = price_repository.get_date_prices(db_session, target_date=date.fromisoformat("2027-01-16"),
                                              currency="btc_usd")

    assert isinstance(prices, list)
    assert len(prices) == 0
