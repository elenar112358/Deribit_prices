from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models import Currency, IndexPrice
from app.schemas import PricesLineResponse, PricesResponse
from app.service import price_service


def test_check_currency(db_session, saved_prices):
    assert price_service.check_currency(db_session, currency="btc_usd") is None

    with pytest.raises(HTTPException) as exc_info:
        price_service.check_currency(db_session, "unknown_currency")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Currency 'unknown_currency' not found"


def test_get_prices(db_session, saved_prices):
    with pytest.raises(HTTPException) as exc_info:
        price_service.get_prices(db_session, "unknown_currency")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Currency 'unknown_currency' not found"

    prices = price_service.get_prices(db_session, currency="btc_usd")

    assert isinstance(prices, PricesLineResponse)
    assert prices.currency == "btc_usd"
    assert prices.prices == [Decimal("65000.25"), Decimal("65100.50")]
    assert prices.timestamps == [1_800_000_001, 1_800_000_002]


def test_get_last_price(db_session, saved_prices):
    with pytest.raises(HTTPException) as exc_info:
        price_service.get_prices(db_session, "unknown_currency")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Currency 'unknown_currency' not found"

    price = price_service.get_last_price(db_session, currency="btc_usd")

    assert isinstance(price, PricesResponse)
    assert price.currency == "btc_usd"
    assert price.price == Decimal("65100.50")
    assert price.timestamp == 1_800_000_002


def test_get_date_prices(db_session, saved_prices):
    with pytest.raises(HTTPException) as exc_info:
        price_service.get_prices(db_session, "unknown_currency")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Currency 'unknown_currency' not found"

    prices = price_service.get_date_prices(db_session, target_date=date.fromisoformat("2027-01-15"),
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

    prices = price_service.get_date_prices(db_session, target_date=date.fromisoformat("2027-01-16"),
                                           currency="btc_usd")

    assert isinstance(prices, list)
    assert len(prices) == 0


def test_parse_price(json_response):
    price, timestamp = price_service.parse_price(json_response)

    assert price == Decimal("82306.64")
    assert timestamp == 1792079447


def test_save_prices_existing_currency(db_session, saved_prices, fetched_prices, monkeypatch):
    monkeypatch.setattr(
        price_service,
        "SessionLocal",
        lambda: db_session,
    )

    price_service.save_prices(fetched_prices)

    currency = db_session.query(Currency).filter_by(ticker="btc_usd").one()
    prices = db_session.query(IndexPrice).filter_by(currency_id=currency.id).all()

    assert len(prices) == 3
    assert prices[-1].price == Decimal("65103.71")
    assert prices[-1].timestamp == 1_800_000_003

    currency = db_session.query(Currency).filter_by(ticker="eth_usd").one()
    prices = db_session.query(IndexPrice).filter_by(currency_id=currency.id).all()

    assert len(prices) == 1
    assert prices[-1].price == Decimal("80000.00")
    assert prices[-1].timestamp == 1_800_000_001


def test_save_prices_new_currency(db_session, fetched_prices, monkeypatch):
    monkeypatch.setattr(
        price_service,
        "SessionLocal",
        lambda: db_session,
    )

    price_service.save_prices(fetched_prices)

    currency = db_session.query(Currency).filter_by(ticker="btc_usd").one()
    price = db_session.query(IndexPrice).filter_by(currency_id=currency.id).one()

    assert currency.ticker == "btc_usd"
    assert price.price == Decimal("65103.71")
    assert price.timestamp == 1_800_000_003

    currency = db_session.query(Currency).filter_by(ticker="eth_usd").one()
    price = db_session.query(IndexPrice).filter_by(currency_id=currency.id).one()

    assert currency.ticker == "eth_usd"
    assert price.price == Decimal("80000.00")
    assert price.timestamp == 1_800_000_001
