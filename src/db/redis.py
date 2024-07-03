import redis.asyncio
from redis import Redis

from src.core.config import app_settings

redis: Redis = redis.asyncio.from_url(app_settings.redis_url)


async def get_redis() -> Redis:
    return redis
