from app.models import Currency
from app.repository import currency_repository

from uuid import UUID


def test_currency_exists(db_session, saved_prices):
    assert currency_repository.currency_exists(db_session, ticker="btc_usd") == True
    assert currency_repository.currency_exists(db_session, ticker="eth_usd") == False


def test_get_currency_id(db_session, saved_prices):
    currency_id = saved_prices["currency_id"]

    assert currency_repository.get_currency_id(db_session, ticker="btc_usd") == currency_id
    assert currency_repository.get_currency_id(db_session, ticker="eth_usd") is None


def test_create_currency(db_session, saved_prices):
    currency_id = currency_repository.create_currency(db_session, ticker="eth_usd")

    assert isinstance(currency_id, UUID)

    currency = db_session.get(Currency, currency_id)

    assert currency is not None
    assert currency.ticker == "eth_usd"