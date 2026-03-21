from celery import group, chain

from celery_app import celery_app
from app.tasks.parse_sites import parse_site_task
from app.tasks.parse_channels import parse_channels_task
from app.tasks.generate import generate_post_task
from app.tasks.filter import filter_posts_task
from app.redis_sync import get_sync_redis


def get_rss_source_names():
    redis = get_sync_redis()
    keys = redis.keys("site_sources:*")
    return [
        key.split(":")[1]
        for key in keys
    ]

def get_tg_source_names():
    redis = get_sync_redis()
    keys = redis.keys("tg_sources:*")
    return [
        key.split(":")[1]
        for key in keys
    ]


def main():
    # --- Парсинг -----------------------------------------------------
    # --- RSS ---------------------------------------------------------
    rss_source_names = get_rss_source_names()

    if not rss_source_names:
        print("Нет источников")
        return

    parse_rss_group = group(
        parse_site_task.s(source_name=name)
        for name in rss_source_names
    )

    rss_result = parse_rss_group.apply_async()

    print("Задачи запущены. Ждём результата...")

    rss_total = rss_result.get(timeout=300)  # ждём завершения всех
    print("Парсинг RSS запущен. Ждём результата...")
    print(f"Результаты: {rss_total}")
    print(f'Всего сохранено "сырых" постов: {sum(rss_total)}')

    # --- TG ---------------------------------------------------------
    tg_source_names = get_tg_source_names()

    if not tg_source_names:
        print("Нет источников")
        return

    parse_tg_group = group(
        parse_channels_task.s(source_name=name)
        for name in tg_source_names
    )

    tg_result = parse_tg_group.apply_async()

    tg_total = tg_result.get(timeout=300)  # ждём завершения всех
    print("Парсинг TG запущен. Ждём результата...")
    print(f"Результаты: {tg_total}")
    print(f'Всего сохранено "сырых" постов: {sum(tg_total)}')

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
    # ToDo: Сделать пайплайн публикации


if __name__ == "__main__":
    main()