import redis

from app.core.config import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL or "redis://localhost:6379", decode_responses=True
)


def get_redis_client():
    return redis_client


def test_redis_connection() -> bool:
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False
