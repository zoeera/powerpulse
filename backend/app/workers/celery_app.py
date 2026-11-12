from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "powerpulse_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.ocr_tasks",
        "app.workers.cron_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "auto-delete-24-month-retention-daily": {
            "task": "app.workers.cron_tasks.purge_expired_data_task",
            "schedule": 86400.0,  # Run once every 24 hours
        },
    }
)

