from celery import Celery

celery_app = Celery(
    "price_collector",
    broker="redis://localhost:6379/0",
    include=["app.tasks.price_task"],
)

celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.price_task.fetch_prices",
        "schedule": 60.0,
    },
}

celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

"""
celery -A app.core.celery_app:celery_app worker --loglevel=INFO --pool=solo

celery -A app.core.celery_app:celery_app beat --loglevel=INFO
"""