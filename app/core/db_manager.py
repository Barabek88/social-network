"""Database connection manager for read/write routing."""

import random
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from app.settings import settings
from app.core.database import make_url_async
from app.logger import logger


class DatabaseManager:
    def __init__(self):
        # Master (write) engine
        self.write_engine: AsyncEngine = create_async_engine(
            make_url_async(settings.DATABASE_URL),
            pool_size=settings.POSTGRES_POOl_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
            pool_recycle=settings.POSTGRES_POOL_RECYCLE,
        )

        # Read replica engines (dynamic from environment)
        self.read_engines: list[AsyncEngine] = [
            create_async_engine(
                make_url_async(url),
                pool_size=settings.POSTGRES_POOl_SIZE,
                max_overflow=settings.POSTGRES_MAX_OVERFLOW,
                pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
                pool_recycle=settings.POSTGRES_POOL_RECYCLE,
            )
            for url in settings.get_read_replica_urls
        ]

        # Session makers
        self.write_session_maker = async_sessionmaker(
            bind=self.write_engine, expire_on_commit=False
        )
        self.read_session_makers = [
            async_sessionmaker(bind=engine, expire_on_commit=False)
            for engine in self.read_engines
        ]

        # Health status tracking
        self.healthy_read_engines = list(range(len(self.read_engines)))
        self._health_check_task = None

    async def _health_check(self):
        """Periodically check replica health."""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            healthy_engines = []

            for i, engine in enumerate(self.read_engines):
                try:
                    async with engine.begin() as conn:
                        await conn.execute(text("SELECT 1"))
                    healthy_engines.append(i)
                    logger.debug(f"Replica {i} is healthy")
                except Exception as e:
                    logger.warning(f"Replica {i} is unhealthy: {e}")

            self.healthy_read_engines = healthy_engines
            if not self.healthy_read_engines:
                logger.error("All read replicas are down!")

    async def start_health_check(self):
        """Start health check background task."""
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self._health_check())

    async def stop_health_check(self):
        """Stop health check background task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

    async def get_write_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get session for write operations (master)."""
        logger.info(
            f"Routing WRITE query to master: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
        )
        async with self.write_session_maker() as session:
            yield session

    async def get_read_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get session for read operations (healthy replica or fallback to master)."""
        if not self.healthy_read_engines:
            logger.warning("No healthy replicas, falling back to master")
            async with self.write_session_maker() as session:
                yield session
            return

        # Choose random healthy replica
        replica_index = random.choice(self.healthy_read_engines)
        replica_url = settings.get_read_replica_urls[replica_index]
        replica_host = (
            replica_url.split("@")[1]
            if "@" in replica_url
            else replica_url.split("//")[1]
        )
        logger.info(f"Routing READ query to replica {replica_index}: {replica_host}")

        session_maker = self.read_session_makers[replica_index]

        try:
            async with session_maker() as session:
                yield session
        except Exception as e:
            logger.error(f"Replica {replica_index} failed during query: {e}")
            # Remove from healthy list and fallback to master
            if replica_index in self.healthy_read_engines:
                self.healthy_read_engines.remove(replica_index)

            logger.warning("Falling back to master for read operation")
            async with self.write_session_maker() as session:
                yield session

    async def close_all(self):
        """Close all database connections."""
        await self.stop_health_check()
        await self.write_engine.dispose()
        for engine in self.read_engines:
            await engine.dispose()


# Global instance
db_manager = DatabaseManager()
