from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repository import currency_repository, price_repository
from app.schemas import PricesResponse, PricesLineResponse

import aiohttp
import asyncio

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


async def fetch_index_price(client: aiohttp.ClientSession, ticker: str) -> dict[str, Any]:
    async with client.get(
            DERIBIT_URL,
            params={"index_name": ticker},
    ) as response:
        response.raise_for_status()
        data = await response.json()

    if "error" in data:
        raise RuntimeError(
            f"Deribit API error for {ticker}: {data['error']}"
        )

    return data


def parse_price(data: dict[str, Any]) -> tuple[Decimal, int]:
    price = Decimal(str(data["result"]["index_price"]))
    timestamp = int(data["usIn"]) // 1_000_000

    return price, timestamp


async def get_parsed_price(client: aiohttp.ClientSession, ticker: str) -> tuple[Decimal, int]:
    data = await fetch_index_price(client, ticker)

    return parse_price(data)


async def fetch_prices() -> dict[str, tuple[Decimal, int]]:
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as client:
        results = await asyncio.gather(
            *(
                get_parsed_price(client, ticker)
                for ticker in TICKERS
            )
        )

    return dict(zip(TICKERS, results))


def save_prices(prices: dict[str, tuple[Decimal, int]]) -> None:
    with SessionLocal() as db:
        with db.begin():
            for ticker, (price, timestamp) in prices.items():
                currency_id = currency_repository.get_currency_id(db, ticker)

                if currency_id is None:
                    currency_id = currency_repository.create_currency(db, ticker)

                price_repository.create_index_price(
                    db=db,
                    currency_id=currency_id,
                    price=price,
                    timestamp=timestamp,
                )


async def fetch_and_save_prices() -> None:
    prices = await fetch_prices()
    save_prices(prices)


def check_currency(db: Session, currency: str) -> None:
    if not currency_repository.currency_exists(db, currency):
        raise HTTPException(
            status_code=404,
            detail=f"Currency '{currency}' not found",
        )


def get_prices(db: Session, currency: str) -> PricesLineResponse:
    check_currency(db, currency)

    return price_repository.get_prices(db, currency)


def get_last_price(db: Session, currency: str) -> PricesResponse | None:
    check_currency(db, currency)

    return price_repository.get_last_price(db, currency)


def get_date_prices(db: Session, target_date: date, currency: str) -> list[PricesResponse]:
    check_currency(db, currency)

    return price_repository.get_date_prices(db, target_date, currency)
