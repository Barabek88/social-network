import redis.asyncio as redis
from app.settings import settings
from app.logger import logger


class RedisClient:
    def __init__(self):
        self.client: redis.Redis | None = None

    async def connect(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    def get_client(self) -> redis.Redis:
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        return self.client


redis_client = RedisClient()
