from celery_app import app
import time

@app.task
def add(x, y):
    time.sleep(10)  # Небольшая задержка для демонстрации
    return x + y