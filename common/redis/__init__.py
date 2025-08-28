"""Базовый клиент redis."""
from typing import Any

from redis.asyncio import ConnectionPool, Redis


class BaseRedis:
    """Базовый клиент redis."""

    def __init__(
        self,
        redis_pool: ConnectionPool,
    ) -> None:
        self.redis_pool = redis_pool

    async def get(self, key: str) -> bytes | None:
        """
        Получить данные из redis.

        :param key: ключ в redis.
        :returns: Данные из redis.
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            return await redis.get(key)

    async def set(self, key: str, value: Any, ex: int) -> None:  # noqa: WPS110
        """
        Положить данные в redis.

        :param key: ключ в redis.
        :param value: Значение в redis.
        :param ex: Время протухания в redis.
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            await redis.set(key, value, ex=ex)
