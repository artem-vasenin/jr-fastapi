import time
from celery_app import app


@app.task
def demo_task(name, duration=2):
    print(f"START {name}")
    time.sleep(duration)
    print(f"END   {name}")