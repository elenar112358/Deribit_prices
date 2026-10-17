from sqlalchemy.util.typing import SupportsKeysAndGetItem

"""   
- обработка мок-ответа от биржи: 
-- парсинг цены (parse_price)
-- создание валюты в базе если ее не было (save_prices)
-- добавление новой цены для валюты (save_prices)

- обработка трех get api: "/prices/", "/last_price/", "/date_prices/":
-- при несуществующей валюте возвращается 404
-- возвращение корректных данных

- проверка price_service: check_currency, get_prices, get_last_price, get_date_prices

- currency_repository: currency_exists, get_currency_id, create_currency

- price_repository: create_index_price, get_prices, get_last_price, get_date_prices
"""

