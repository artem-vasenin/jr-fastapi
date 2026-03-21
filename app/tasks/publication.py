from celery import shared_task

from app.utils.logging import get_logger
from app.redis_sync import get_sync_redis
from app.services.publish import post_to_channel


logger = get_logger(__name__)

@shared_task(bind=True, name="public_post", max_retries=2)
def public_post_task(self, key: str):
    """Публикация AI-поста."""
    redis = get_sync_redis()

    try:
        data = redis.hgetall(key)
        if not data:
            logger.warning(f"Сгенерированная новость не найдена: {key}")
            return 0

        title = data.get("new_title", "")
        summary = data.get("generated_post", "")
        source = data.get("source", "unknown")
        published_at_str = data.get("generated_at", "")

        post_to_channel(title, summary, source, published_at_str)

        logger.info("Пост опубликован")
        return 1
    except Exception as e:
        logger.exception(f"Ошибка публикации поста для {key}")
        raise self.retry(exc=e, countdown=60)