from aiohttp import ClientConnectorError
from miniopy_async import S3Error
from redis import RedisError
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import logger
from src.services.minio import MinioHandler


async def check_database_status(db: AsyncSession) -> bool:
    """
    Проверка статуса postgres
    """

    try:
        await db.execute(text('SELECT 1'))
        return True
    except (SQLAlchemyError, ConnectionRefusedError) as e:
        logger.error(f'Postgres error occurred: {e}')

        return False


async def check_redis_status(cache: Redis) -> bool:
    """
    Проверка статуса redis
    """

    try:
        await cache.ping()
        return True
    except RedisError as e:
        logger.error(f'Redis error occurred: {e}')
        return False


async def check_minio_status() -> bool:
    """
    Проверка статуса minio
    """

    try:
        minio_handler = MinioHandler()
        buckets = await minio_handler.minio_client.list_buckets()
        if buckets:
            return True
    except (ClientConnectorError, S3Error) as e:
        logger.error(f'Minio error occurred: {e}')

    return False
