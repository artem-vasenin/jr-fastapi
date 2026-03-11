from celery import Celery

app = Celery(
    "rabbitmq_example",
    broker="amqp://guest:guest@localhost:5672//",  # ← на хосте используем localhost
    # Если воркер внутри docker-сети — замените на rabbitmq:5672
    # broker="amqp://guest:guest@rabbitmq:5672//",

    backend="rpc://",  # результаты возвращаются через RabbitMQ (просто для тестов)
    # Альтернатива: backend="redis://localhost:6379/0" — если добавить redis в compose

    include=["tasks"],
)

# Полезные настройки (почти без изменений)
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=29 * 60,
    result_expires=3600,  # результаты храним 1 час
    worker_concurrency=2,

    # Рекомендации для RabbitMQ в Docker
    broker_connection_retry_on_startup=True,
    broker_heartbeat=0,  # часто отключают в контейнерах
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)