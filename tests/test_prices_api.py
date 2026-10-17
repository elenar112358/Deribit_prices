from app.schemas import PricesLineResponse


def test_get_prices_unknown_currency(client):
    response = client.get(
        "/api/prices/",
        params={"currency": "unknown_currency"},
    )

    assert response.status_code == 404


def test_get_prices(client, saved_prices):
    response = client.get(
        "/api/prices/",
        params={"currency": "btc_usd"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "currency": "btc_usd",
        "prices": ["65000.25", "65100.50"],
        "timestamps": [1_800_000_001, 1_800_000_002],
    }


def test_get_last_price_unknown_currency(client):
    response = client.get(
        "/api/prices/",
        params={"currency": "unknown_currency"},
    )

    assert response.status_code == 404


def test_get_last_price(client, saved_prices):
    response = client.get(
        "/api/last_price/",
        params={"currency": "btc_usd"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "currency": "btc_usd",
        "price": "65100.50",
        "timestamp": 1_800_000_002,
    }


"""   

- обработка трех get api: "/prices/", "/last_price/", "/date_prices/":
-- при несуществующей валюте возвращается 404
-- возвращение корректных данных

docker compose -f compose.test.yml run --build --rm test pytest -v tests/test_prices_api.py

"""
