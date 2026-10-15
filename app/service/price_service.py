import time
from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repository.currency_repository import get_currency_id, create_currency
from app.repository.price_repository import create_index_price


DERIBIT_URL = (
    "https://test.deribit.com/api/v2/public/get_index_price"
)

TICKERS = ("btc_usd", "eth_usd")

"""
curl --request GET \
  --url "https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd"
  
{
    "jsonrpc":"2.0",
    "result":{
        "estimated_delivery_price":82306.64,
        "index_price":82306.64
    },
    "usIn":1792079447881029,
    "usOut":1792079447881337,
    "usDiff":308,
    "testnet":true
}

{
    "jsonrpc":"2.0",
    "error":{
        "code":-32602,
        "data":{
            "reason":"value required",
            "param":"index_name"
        },
        "message":"Invalid params"
    },
    "testnet":true,
    "usIn":1792079316915536,
    "usOut":1792079316915632,
    "usDiff":96
}
"""


def fetch_index_price(
    client: httpx.Client,
    ticker: str,
) -> tuple[Decimal, int]:
    response = client.get(
        DERIBIT_URL,
        params={"index_name": ticker},
    )
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(
            f"Deribit API error for {ticker}: {data['error']}"
        )

    price = Decimal(str(data["result"]["index_price"]))
    timestamp = int(data["usIn"]) // 1_000_000

    return price, timestamp


def fetch_and_save_prices() -> None:
    with httpx.Client(timeout=10.0) as client:
        prices = {
            ticker: fetch_index_price(client, ticker)
            for ticker in TICKERS
        }

    with SessionLocal() as db:
        with db.begin():
            for ticker, (price, timestamp) in prices.items():
                currency_id = get_currency_id(db, ticker)

                if currency_id is None:
                    currency_id = create_currency(db, ticker)

                create_index_price(
                    db=db,
                    currency_id=currency_id,
                    price=price,
                    timestamp=timestamp,
                )