from app.core.celery_app import celery_app
from app.service.price_service import fetch_and_save_prices


@celery_app.task(name="app.tasks.price_task.fetch_prices")
def fetch_prices():
    fetch_and_save_prices()