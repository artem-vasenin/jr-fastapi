from celery import group

from celery_app import celery_app
from app.tasks.parse_sites import parse_site_task
from app.redis_sync import get_sync_redis


def get_all_source_names():
    redis = get_sync_redis()
    keys = redis.keys("site_sources:*")
    return [
        key.split(":")[1]
        for key in keys
    ]


def main():
    source_names = get_all_source_names()

    if not source_names:
        print("Нет источников")
        return

    parse_group = group(
        parse_site_task.s(source_name=name)
        for name in source_names
    )

    result = parse_group.apply_async()

    print("Задачи запущены. Ждём результата...")

    total = result.get(timeout=300)  # ждём завершения всех
    print(f"Результаты: {total}")
    print(f"Всего сохранено: {sum(total)}")

if __name__ == "__main__":
    main()