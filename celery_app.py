from celery import Celery

# Обычно выносят в отдельный модуль
app = Celery(
    "simple_example",
    broker="redis://localhost:6379/0",   # В production localhost заменить на redis
    backend="redis://localhost:6379/0",  # В production localhost заменить на redis
    include=["tasks"],          # модуль с задачами
)

# Полезные настройки по умолчанию
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,          # 30 минут
    task_soft_time_limit=29 * 60,
    result_expires=3600,              # результаты храним 1 час
    worker_concurrency=2,
)