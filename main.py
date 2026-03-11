from fastapi import FastAPI
from celery.result import AsyncResult

from tasks import add

app = FastAPI()


@app.get("/run-task/")
async def run_task():
    """
    Плохой синхронный вариант для демонстрации
    """
    task = add.delay(4, 5)
    result = task.get(timeout=10.5)  # Ждём результат с таймаутом
    return {'task_id': task.id, 'result': result}


@app.get("/run-task-async/")
async def run_task_async():
    """
    Хороший асинхронный вариант для продакшн
    1. В этом эндпоинте мы только отправляем задачу на исполнение.
    2. А результат смотрим через http://127.0.0.1:8000/task-status/9a501c03-9a54-4399-a6c7-a37bb1baf534/
    ГЛАВНОЕ: не забыть взять из респонса id задачи!
    """
    task = add.delay(4, 5)
    return {'task_id': task.id, 'status': 'started'}


@app.get("/task-status/{task_id}")
async def task_status(task_id: str):
    """
    Получаем статус задачи после её реального выполнения.
    ГЛАВНОЕ: не забыть взять из респонса id задачи!
    """
    result = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': result.status,
    }

    if result.ready():
        response['result'] = result.result

    return response