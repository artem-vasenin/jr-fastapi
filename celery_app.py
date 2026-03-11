from celery import Celery

app = Celery(
    'celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']
)

app.conf.update(
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json'
)