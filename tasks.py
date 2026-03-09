from celery_app import app
import time

@app.task
def add(x, y):
    """Простая задача для теста"""
    time.sleep(3)  # имитируем долгую работу
    result = x + y
    print(f"Задача выполнена: {x} + {y} = {result}")
    return result

@app.task(bind=True, max_retries=3, default_retry_delay=5)
def flaky_task(self):
    """Задача, которая иногда падает"""
    x = time.time() % 2  # ~50% шанс упасть
    print(f'time.time() % 2 = {x}')
    if x > 1:
        raise self.retry(exc=ValueError("Ой, упал!"))
    return "Всё ок!"

# Параметры декоратора @app.task():
# bind=True → даёт доступ к self.retry() и информации о попытках
# max_retries=3 → сколько раз можно перепробовать (всего запусков = 1 + 3)
# default_retry_delay=5 → сколько секунд ждать между попытками
