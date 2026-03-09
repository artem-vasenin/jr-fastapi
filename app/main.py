from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.rabbit import publish, consume_forever, get_connection
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI + RabbitMQ (упрощённо)")


async def example_processor(body: str):
    logger.info(f"Обработка: {body}")
    await asyncio.sleep(5.0)  # имитация
    logger.info(f"Обработано: {body}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    conn = await get_connection()  # инициализируем подключение заранее
    consumer_task = asyncio.create_task(consume_forever(example_processor))
    logger.info("FastAPI запущен, consumer запущен")

    yield

    # shutdown — graceful
    logger.info("Shutdown: отменяем consumer...")
    consumer_task.cancel()
    try:
        await asyncio.wait_for(consumer_task, timeout=5.0)
        logger.info("Consumer gracefully завершён")
    except asyncio.TimeoutError:
        logger.warning("Consumer не завершился за 5 сек — forceful cancel")
    except asyncio.CancelledError:
        pass

    # Закрываем глобальное подключение
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
        logger.info("RabbitMQ соединение закрыто")


app.router.lifespan_context = lifespan


class Message(BaseModel):
    content: str


@app.post("/send/")
async def send_to_queue(msg: Message, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish, msg.content)
    return {"status": "Сообщение отправлено"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
