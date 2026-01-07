from redis.asyncio import Redis, ConnectionPool
from apps.core.settings import settings


class RedisDependency:
    def __init__(self):
        self._pool: ConnectionPool | None = None

    async def _get_pool(self) -> ConnectionPool:
        if self._pool is None:
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                encoding="utf-8",
                max_connections=20,
            )
        return self._pool

    async def client(self) -> Redis:
        pool = await self._get_pool()
        redis_client: Redis = Redis(connection_pool=pool)
        return redis_client

    async def close(self):
        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None
