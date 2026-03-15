from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies import get_redis
from app.schemas.site_sources import SiteSourceCreate, SiteSourceUpdate, SiteSourceOut
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/site_sources",
    tags=["site_sources"],
    responses={404: {"description": "Source not found"}},
)

@router.get("/", response_model=list[SiteSourceOut])
async def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    redis = Depends(get_redis),
):
    """Получить список всех источников сайтов"""
    logger.debug(f"Запрос списка источников: skip={skip}, limit={limit}")

    sources = []

    try:
        # Получаем все ключи site_sources
        keys = await redis.keys("site_sources:*")
        if not keys:
            return []  # если ключей нет, возвращаем пустой список

        for key in sorted(keys)[skip : skip + limit]:
            # Декодируем ключ, если он bytes
            key_str = key.decode() if isinstance(key, bytes) else key

            # Берем все поля HASH как словарь str → str
            data = await redis.hgetall(key_str)
            if not data:
                logger.warning(f"HASH ключ пуст или неверный формат: {key_str}")
                continue

            name = data.get("name")
            url = data.get("url")
            if name and url:
                sources.append(SiteSourceOut(name=name, url=url))
            else:
                logger.warning(f"HASH ключ не содержит необходимых полей: {key_str}")

        return sources

    except Exception:
        logger.exception("Ошибка при получении списка источников")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching site sources",
        )


@router.get("/{name}", response_model=SiteSourceOut)
async def get_source(name: str, redis = Depends(get_redis)):
    """Получить один источник сайта по имени"""
    key = f"site_sources:{name}"
    exists = await redis.exists(key)
    if not exists:
        raise HTTPException(404, "Source not found")

    data = await redis.hgetall(key)
    name_s = data.get("name")
    url_s = data.get("url")
    if not name_s or not url_s:
        raise HTTPException(500, "Invalid source data in Redis")

    return SiteSourceOut(
        name=name_s,
        url=url_s
    )


@router.post("/", response_model=SiteSourceOut, status_code=201)
async def create_source(data: SiteSourceCreate, redis = Depends(get_redis)):
    key = f"site_sources:{data.name}"
    if await redis.exists(key):
        raise HTTPException(409, f"Source '{data.name}' already exists")

    try:
        # Конвертируем HttpUrl в str
        await redis.hset(key, mapping={"name": data.name, "url": str(data.url)})
        return SiteSourceOut(name=data.name, url=str(data.url))

    except Exception:
        logger.exception(f"Ошибка при создании источника {data.name}")
        raise HTTPException(500, "Failed to create site source")


@router.patch("/{name}", response_model=SiteSourceOut)
async def update_source(name: str, data: SiteSourceUpdate, redis = Depends(get_redis)):
    key = f"site_sources:{name}"
    if not await redis.exists(key):
        raise HTTPException(404, "Source not found")

    current = await redis.hgetall(key)
    current_name = current.get("name")
    current_url = current.get("url")
    if not current_name or not current_url:
        raise HTTPException(500, "Invalid source data in Redis")

    new_name = data.name.strip() if data.name else current_name
    new_url = str(data.url) if data.url else current_url

    if new_name != name and await redis.exists(f"site_sources:{new_name}"):
        raise HTTPException(409, f"Source '{new_name}' already exists")

    try:
        if new_name != name:
            await redis.delete(key)
            key = f"site_sources:{new_name}"

        await redis.hset(key, mapping={"name": new_name, "url": new_url})
        return SiteSourceOut(name=new_name, url=new_url)

    except Exception:
        logger.exception(f"Ошибка при обновлении источника {name} → {new_name}")
        raise HTTPException(500, "Failed to update site source")


@router.delete("/{name}", status_code=204)
async def delete_source(name: str, redis = Depends(get_redis)):
    key = f"site_sources:{name}"
    removed = await redis.delete(key)
    if removed == 0:
        raise HTTPException(404, "Source not found")

    logger.info(f"Источник сайта удалён: {name}")
    return None
