from celery import Celery

celery_app = Celery(
    "bg-removal",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
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
