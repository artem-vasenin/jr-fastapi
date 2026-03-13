from celery import Celery
from kombu import Queue

BROKER = "amqp://guest:guest@localhost:5672//"
# BROKER = "redis://localhost:6379/0"

app = Celery(
    "priority_demo",
    broker=BROKER,
    backend="redis://localhost:6379/1",
    include=["tasks"],
)

app.conf.update(
    # ===== Очереди =====
    task_queues=(
        # Для RabbitMQ priority
        Queue(
            "priority",
            routing_key="priority",
            queue_arguments={
                "x-max-priority": 10,
            },
        ),

        # Для Redis-приоритетов через очереди
        Queue("high"),
        Queue("default"),
        Queue("low"),
    ),

    task_default_queue="default",

    # ===== КРИТИЧНО для демонстрации =====
    worker_prefetch_multiplier=1,
    task_acks_late=True,

    task_serializer="json",
    accept_content=["json"],
    worker_concurrency=1,   # Чтобы задачи шли строго последовательно
)