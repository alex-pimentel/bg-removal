import os

from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "bg-removal",
    broker=os.environ.get("CELERY_BROKER_URL", REDIS_URL),
    backend=os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL),
    include=["src.tasks.remove_bg"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)
