import redis.asyncio as redis
from typing import AsyncGenerator
from app.core.config import settings

# Global variables for the Redis connection pool
redis_client: redis.Redis = None

async def init_redis():
    global redis_client
    if settings.REDIS_ENABLED:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """FastAPI dependency to get the redis connection."""
    yield redis_client
