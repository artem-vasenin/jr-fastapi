import asyncio
import logging

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractRobustConnection
from app.config import RABBITMQ_URL, QUEUE_NAME

logger = logging.getLogger(__name__)

_connection: AbstractRobustConnection | None = None


async def get_connection() -> AbstractRobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(RABBITMQ_URL)
        logger.info("Подключение к RabbitMQ установлено")
    return _connection


async def publish(message: str):
    conn = await get_connection()
    async with conn.channel() as ch:
        await ch.default_exchange.publish(
            Message(
                body=message.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )
    logger.info(f"Опубликовано: {message}")


async def consume_forever(process_func):
    """Простой consumer без while True — lifespan сам управляет"""
    conn = await get_connection()
    async with conn.channel() as ch:
        await ch.set_qos(prefetch_count=1)

        queue = await ch.declare_queue(
            QUEUE_NAME,
            durable=True,
            arguments={"x-queue-type": "classic"}
        )

        async def on_msg(msg: aio_pika.IncomingMessage):
            async with msg.process(requeue=True):
                body = msg.body.decode(errors="replace")
                logger.info(f"Получено: {body}")
                await process_func(body)

        await queue.consume(on_msg, no_ack=False)
        logger.info(f"Консьюмер запущен на очереди {QUEUE_NAME}")

        # Держим открытым до отмены задачи (lifespan отменит)
        await asyncio.sleep(float("inf"))  # или await conn.connected.wait()
