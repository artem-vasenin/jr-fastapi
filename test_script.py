from celery_app import app
from tasks import add, flaky_task

if __name__ == "__main__":
    # Отправляем задачу
    res1 = add.delay(7, 11)
    print("Задача add отправлена, id =", res1.id)

    # Можно сразу ждать результат (не рекомендуется в продакшене)
    print("Результат:", res1.get(timeout=10))

    # Цепочка задач
    res2 = add.s(100, 200) | add.s(300)
    chained = res2.delay()
    print("Цепочка отправлена, id =", chained.id)

    # Задача с ретраями
    flaky_task.delay()