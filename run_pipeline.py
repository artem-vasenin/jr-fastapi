from typing import Any

from celery import group, chain

from celery_app import celery_app
from app.tasks.parse_sites import parse_site_task
from app.tasks.parse_channels import parse_channels_task
from app.tasks.generate import generate_post_task
from app.tasks.filter import filter_posts_task
from app.tasks.publication import public_post_task
from app.redis_sync import get_sync_redis


def get_source_names(target: str):
    redis = get_sync_redis()
    keys = redis.keys(target)

    return [key.split(":")[1] for key in keys]


def parse_sources(target: str, task: Any, p_type: str):
    source_names = get_source_names(target)

    if not source_names:
        print("Нет источников")
        return

    parse_group = group(task.s(source_name=name) for name in source_names)
    result = parse_group.apply_async()

    print("Задачи запущены. Ждём результата...")

    total = result.get(timeout=300)  # ждём завершения всех
    print(f"Парсинг {p_type} запущен. Ждём результата...")
    print(f"Результаты: {total}")
    print(f'Всего сохранено "сырых" постов: {sum(total)}')


def main():
    # --- Парсинг RSS ---------------------------------------------------------
    parse_sources("site_sources:*", parse_site_task, "RSS")

    # --- Парсинг TG ---------------------------------------------------------
    parse_sources("tg_sources:*", parse_channels_task, "TG")

    # --- Фильтрация --------------------------------------------------
    filter_result = filter_posts_task.apply_async()
    print("Фильтрация запущена. Ждём результата...")

    filtered_count = filter_result.get(timeout=180)
    print(f"Отфильтровано: {filtered_count}")

    # --- Запуск генерации постов -------------------------------------
    redis = get_sync_redis()
    filtered_keys = redis.keys("news:filtered:*")

    if not filtered_keys:
        print("Нет отфильтрованных новостей для генерации")
    else:
        print(f"Найдено отфильтрованных новостей: {len(filtered_keys)}")
        print("Генерация запущена. Ждём результата...")

        generate_group = group(
            generate_post_task.s(
                key.decode("utf-8") if isinstance(key, bytes) else key
            )
            for key in filtered_keys
        )

        try:
            gen_counts = generate_group.apply_async().get(timeout=600)
            total_generated = sum(x or 0 for x in gen_counts)
            print(f"Генерация завершена. Успешно сгенерировано: {total_generated}")
        except Exception as e:
            print(f"Ошибка при генерации: {type(e).__name__}: {e}")

    # --- Публикация сгенерированных постов в тг канале пользователя ----
    generated_keys = redis.keys("news:generated:*")

    if not generated_keys:
        print("Нет сгенерированных новостей для публикации")
    else:
        print(f"Найдено сгенерированных новостей: {len(generated_keys)}")
        print("Публикация запущена. Ждём результата...")

        publish_group = group(
            public_post_task.s(
                key.decode("utf-8") if isinstance(key, bytes) else key
            )
            for key in generated_keys
        )

        try:
            pub_counts = publish_group.apply_async().get(timeout=600)
            total_published = sum(x or 0 for x in pub_counts)
            print(f"Публикация завершена. Успешно опубликовано: {total_published}")
        except Exception as e:
            print(f"Ошибка при публикации: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()