from app.core.celery_app import celery_app
from app.service import price_service

import asyncio


@celery_app.task(name="app.tasks.price_task.fetch_prices")
def fetch_prices():
    asyncio.run(price_service.fetch_and_save_prices())
