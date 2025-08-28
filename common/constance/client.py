"""Базовый клиент redis."""
import pickle  # noqa: S403
from typing import Any

from fastapi import Depends
from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from common.constance.dependencies import get_constance_pool


class Constance:
    """Базовый клиент redis."""

    _PREFIX: str = "SOME_DB://"

    def __init__(  # noqa: WPS612
        self,
        redis_pool: ConnectionPool = Depends(get_constance_pool),
        defaults: dict[str, str | int] | None = None,
    ) -> None:
        self._redis_pool = redis_pool
        self._defaults: dict[str, str | int] = defaults or {}

    async def _get(self, name: str) -> str | int | None:
        """
        Получения константы из кэша.

        :param name: Название константы
        :return: Значение константы
        """
        redis_key = self._get_key(name)
        async with Redis(connection_pool=self._redis_pool) as redis:
            try:
                redis_value: bytes | None = await redis.get(
                    redis_key,
                )
            except RedisError:
                logger.error(f"Ошибка получения константы {redis_key} из Redis")
                redis_value = None

            if redis_value:
                return self._deserialize(redis_value)
            return self._defaults.get(name)

    @classmethod
    def _get_key(cls, name: str) -> str:
        return f"{cls._PREFIX}{name}"

    @staticmethod
    def _deserialize(redis_bytes: bytes | str) -> Any:
        """
        Преобразуем байты в объект питона.

        :param redis_bytes: байты, которое преобразуем
        :returns: Значение
        """
        if isinstance(redis_bytes, bytes):
            return pickle.loads(redis_bytes)  # noqa: S301
        return redis_bytes
