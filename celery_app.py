from celery import Celery
from app.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "news_parser",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        'app.tasks.parse_sites',
        'app.tasks.parse_channels',
        'app.tasks.filter',
        'app.tasks.generate',
        'app.tasks.publication',
        'app.tasks.run_pipeline',
    ],

)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
celery_app.conf.beat_schedule = {
    "run-pipeline-every-minute": {
        "task": "app.tasks.run_pipeline.run_pipeline_task",
        "schedule": crontab(minute="*/30"),
    },
}