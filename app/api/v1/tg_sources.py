from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_redis
from app.utils.logging import get_logger
from app.redis_sync import get_sync_redis
from app.services.source_service import get_all_tg_sources
from app.schemas.tg_sources import TgSourceCreate, TgSourceUpdate, TgSourceOut

logger = get_logger(__name__)

router = APIRouter(
    prefix="/tg_sources",
    tags=["tg_sources"],
    responses={404: {"description": "Source not found"}},
)

@router.get("/", response_model=list[TgSourceOut])
async def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    redis = Depends(get_sync_redis),
):
    """Получить список всех источников тг каналов"""
    logger.debug(f"Запрос списка источников: skip={skip}, limit={limit}")

    try:
        # Получаем все ключи tg_sources
        sources = await run_in_threadpool(
            get_all_tg_sources,redis,
        )

        return sources[skip : skip + limit]
    except Exception:
        logger.exception("Ошибка при получении списка источников tg каналов")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching tg sources",
        )


@router.get("/{name}", response_model=TgSourceOut)
async def get_source(name: str, redis = Depends(get_redis)):
    """Получить один tg канал по имени"""
    key = f"tg_sources:{name}"
    exists = await redis.exists(key)
    if not exists:
        raise HTTPException(404, "Source not found")

    data = await redis.hgetall(key)
    name_s = data.get("name")
    id_s = data.get("id")
    if not name_s or not id_s:
        raise HTTPException(500, "Invalid source data in Redis")

    return TgSourceOut(
        name=name_s,
        id=id_s
    )


@router.post("/", response_model=TgSourceOut, status_code=201)
async def create_source(data: TgSourceCreate, redis = Depends(get_redis)):
    """Добавить тг канал в базу"""
    key = f"tg_sources:{data.name}"
    if await redis.exists(key):
        raise HTTPException(409, f"Source '{data.name}' already exists")

    try:
        await redis.hset(key, mapping={"name": data.name, "id": data.id})
        return TgSourceOut(name=data.name, id=data.id)

    except Exception:
        logger.exception(f"Ошибка при создании tg источника {data.name}")
        raise HTTPException(500, "Failed to create tg source")


@router.patch("/{name}", response_model=TgSourceOut)
async def update_source(name: str, data: TgSourceUpdate, redis = Depends(get_redis)):
    """Изменить тг канал"""
    key = f"tg_sources:{name}"
    if not await redis.exists(key):
        raise HTTPException(404, "Source not found")

    current = await redis.hgetall(key)
    current_name = current.get("name")
    current_id = current.get("id")
    if not current_name or not current_id:
        raise HTTPException(500, "Invalid source data in Redis")

    new_name = data.name.strip() if data.name else current_name
    new_id = data.id if data.id else current_id

    if new_name != name and await redis.exists(f"site_sources:{new_name}"):
        raise HTTPException(409, f"Source '{new_name}' already exists")

    try:
        if new_name != name:
            await redis.delete(key)
            key = f"tg_sources:{new_name}"

        await redis.hset(key, mapping={"name": new_name, "id": new_id})
        return TgSourceOut(name=new_name, id=new_id)

    except Exception:
        logger.exception(f"Ошибка при обновлении tg источника {name} → {new_name}")
        raise HTTPException(500, "Failed to update tg source")


@router.delete("/{name}", status_code=204)
async def delete_source(name: str, redis = Depends(get_redis)):
    """Удалить тг канал по имени"""
    key = f"tg_sources:{name}"
    removed = await redis.delete(key)
    if removed == 0:
        raise HTTPException(404, "Source not found")

    logger.info(f"Источник tg удалён: {name}")
    return None