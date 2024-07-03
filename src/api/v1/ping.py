from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import naive_utcnow
from src.db.db import get_session
from src.db.redis import get_redis
from src.services.ping import (
    check_database_status,
    check_minio_status,
    check_redis_status,
)

ping_router = APIRouter()


@ping_router.get(
    '/',
    summary='Проверка сервисов',
    description='Проверка статуса доступности связанных сервисов',
)
async def ping(
    db: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_redis),
) -> dict:
    """
    Проверка статуса доступности связанных сервисов
    """

    postgres_status = await check_database_status(db=db)
    redis_status = await check_redis_status(cache=cache)
    minio_status = await check_minio_status()

    return {
        'postgres status': 'OK' if postgres_status else 'not available',
        'redis status': 'OK' if redis_status else 'not available',
        'minio status': 'OK' if minio_status else 'not available',
        'date': naive_utcnow(),
    }
