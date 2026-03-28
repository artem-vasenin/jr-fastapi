from celery import group, chain, chord

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

    return [
        key.split(':')[1] if isinstance(key, str)
        else key.decode().split(':')[1]
        for key in keys
    ]


@celery_app.task
def generate_wrapper(_):
    redis = get_sync_redis()
    keys = redis.keys('news:filtered:*')

    if not keys:
        print('Нет отфильтрованных новостей для генерации')
        return 0

    print(f'Генерация: найдено {len(keys)} новостей')

    job = group(
        generate_post_task.s(
            key.decode('utf-8') if isinstance(key, bytes) else key
        )
        for key in keys
    )

    job.apply_async()

    return len(keys)


@celery_app.task
def publish_wrapper(_):
    redis = get_sync_redis()
    keys = redis.keys('news:generated:*')

    if not keys:
        print('Нет сгенерированных новостей для публикации')
        return 0

    print(f'Публикация: найдено {len(keys)} новостей')

    job = group(
        public_post_task.s(
            key.decode('utf-8') if isinstance(key, bytes) else key
        )
        for key in keys
    )

    job.apply_async()

    return len(keys)


def main():
    rss_sources = get_source_names('site_sources:*')
    tg_sources = get_source_names('tg_sources:*')

    if not rss_sources and not tg_sources:
        print('Нет источников вообще')
        return

    parsing_tasks = []

    if rss_sources:
        print(f'Парсинг RSS: найдено {len(rss_sources)} источников')
        parsing_tasks.extend(
            parse_site_task.s(source_name=name)
            for name in rss_sources
        )

    if tg_sources:
        print(f'Парсинг TG: найдено {len(tg_sources)} источников')
        parsing_tasks.extend(
            parse_channels_task.s(source_name=name)
            for name in tg_sources
        )

    parsing_group = group(parsing_tasks)

    workflow = chain(
        filter_posts_task.s(),
        generate_wrapper.s(),
        publish_wrapper.s(),
    )

    chord(parsing_group)(workflow)


if __name__ == '__main__':
    main()