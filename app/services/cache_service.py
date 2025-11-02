import json
from uuid import UUID
from app.core.redis_client import redis_client
from app.settings import settings
from app.logger import logger


class CacheService:
    FEED_KEY_PREFIX = "feed:"

    @staticmethod
    def _get_feed_key(user_id: UUID) -> str:
        return f"{CacheService.FEED_KEY_PREFIX}{user_id}"

    async def get_feed_from_cache(
        self, user_id: UUID, offset: int, limit: int
    ) -> list[dict] | None:
        try:
            client = redis_client.get_client()
            key = self._get_feed_key(user_id)

            cache_size = await client.llen(key)
            if cache_size == 0:
                return None

            # If request exceeds cache capacity, go to DB
            if offset >= settings.FEED_CACHE_SIZE:
                return None

            # If cache is full (1000 posts) but user wants beyond that, go to DB
            if cache_size >= settings.FEED_CACHE_SIZE and offset + limit > cache_size:
                return None

            # If offset beyond cache size, return empty (no more data exists)
            if offset >= cache_size:
                return []

            cached_data = await client.lrange(key, offset, offset + limit - 1)
            return [json.loads(item) for item in cached_data]
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    async def set_feed_to_cache(self, user_id: UUID, posts: list[dict]) -> bool:
        try:
            client = redis_client.get_client()
            key = self._get_feed_key(user_id)

            await client.delete(key)

            if posts:
                serialized = [json.dumps(post, default=str) for post in posts]
                await client.rpush(key, *serialized)

            await client.expire(key, settings.FEED_CACHE_TTL)

            logger.info(f"Cache updated for user {user_id}: {len(posts)} posts")
            return True
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

    async def invalidate_feed(self, user_id: UUID) -> bool:
        try:
            client = redis_client.get_client()
            key = self._get_feed_key(user_id)
            await client.delete(key)
            logger.info(f"Cache invalidated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def invalidate_feeds_for_friends(self, user_ids: list[UUID]) -> bool:
        try:
            client = redis_client.get_client()
            keys = [self._get_feed_key(uid) for uid in user_ids]
            if keys:
                await client.delete(*keys)
                logger.info(f"Cache invalidated for {len(keys)} users")
            return True
        except Exception as e:
            logger.error(f"Bulk cache invalidation error: {e}")
            return False
