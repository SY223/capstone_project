import json
from redis.asyncio import Redis
from app.core.config import settings

redis_client: Redis | None = None


async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(settings.REDIS_BROKER, decode_responses=True)
    return redis_client


async def cache_get(key: str) -> dict | None:
    redis = await get_redis()
    value = await redis.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value: dict, ttl: int = 60) -> None:
    redis = await get_redis()
    await redis.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    redis = await get_redis()
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)