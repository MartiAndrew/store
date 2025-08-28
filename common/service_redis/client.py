"""Базовый клиент redis."""
from contextlib import asynccontextmanager
from typing import Any, Mapping, Optional, Set

from fastapi import Depends
from loguru import logger
from redis import exceptions as redis_exceptions
from redis.asyncio import ConnectionPool, Redis

from common.redis import BaseRedis
from common.service_redis.dependencies import get_service_redis_pool

from configuration.settings import settings


class ServiceRedis(BaseRedis):
    """Базовый клиент redis."""

    def __init__(  # noqa: WPS612
        self,
        redis_pool: ConnectionPool = Depends(get_service_redis_pool),
    ) -> None:
        super().__init__(redis_pool)

    async def hset(
        self,
        name: str,
        key: str = None,
        cache_value: Any = None,
        mapping: Mapping[str, Any] = None,
    ) -> int:
        """
        Добавляет пару ключ-значение в хеш Redis.

        :param name: Имя хеша в Redis.
        :param key: Ключ в хеше в Redis.
        :param cache_value: Значение в хеше в Redis.
        :param mapping: Пара ключ-значение в формате bytes.
        :raises ValueError: Необходимо передавать key и value или mapping.
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: Количество добавленных элементов.
        """
        try:
            async with Redis(connection_pool=self.redis_pool) as redis:
                if key and cache_value:
                    return await redis.hset(name=name, key=key, value=cache_value)
                elif mapping:
                    return await redis.hset(name=name, mapping=mapping)
                raise ValueError("Необходимо передавать key и value или mapping.")
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка добавления элемента в хеш Redis: {exp}",
                exp_info=True,
            )
            raise

    async def hgetall(self, name: str) -> dict[bytes, bytes]:
        """
        Возвращает все элементы хеша (Redis Hash) по указанному ключу.

        :param name: Ключ хеша в Redis.
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: Словарь элементов хеша в формате bytes.
        """
        try:
            async with Redis(connection_pool=self.redis_pool) as redis:
                return await redis.hgetall(name)
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка получения элементов хеша Redis: {exp}",
                exp_info=True,
            )
            raise

    async def hget(self, name: str, key: str) -> bytes:
        """
        Возвращает значение элемента хеша (Redis Hash) по указанному ключу.

        :param name: Ключ хеша в Redis.
        :param key: Ключ в хеше в Redis.
        :return: Значение элемента хеша в формате bytes.
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            return await redis.hget(name, key)

    async def hdel(self, name: str, key: str) -> int:
        """
        Удаляет элемент хеша (Redis Hash) по указанному ключу.

        :param name: Ключ хеша в Redis.
        :param key: Ключ в хеше в Redis.
        :return: Количество удаленных элементов.
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            return await redis.hdel(name, key)

    async def delete_hash(self, name: str) -> int:
        """
        Удаляет весь хеш (Redis Hash) по его имени.

        :param name: Ключ хеша в Redis.
        :return: Количество удаленных ключей (1 если удален, 0 если ключа не было).
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            return await redis.delete(name)

    async def smembers(
        self,
        name: str,
    ) -> Set[bytes]:
        """
        Возвращает все элементы множества (Redis Set) по указанному ключу.

        :param name: Ключ множества в Redis.
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: Набор элементов множества в формате bytes.
        """
        try:
            async with Redis(connection_pool=self.redis_pool) as redis:
                return await redis.smembers(name)
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка получения элементов множества Redis: {exp}",
                exp_info=True,
            )
            raise

    async def srem(
        self,
        name: str,
        *elements: str,
    ) -> int:
        """
        Удаляет элементы из множества (Redis Set).

        :param name: Ключ множества в Redis.
        :param elements: Элементы множества в формате bytes.
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: Количество удаленных элементов.
        """
        try:
            async with Redis(connection_pool=self.redis_pool) as redis:
                return await redis.srem(name, *elements)
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка удаления элементов множества Redis: {exp}",
                exp_info=True,
            )
            raise

    async def xadd(
        self,
        name: str,
        fields: Mapping[str, Any],
        maxlen: Optional[int] = None,
        approximate: bool = False,
    ) -> bytes:
        """
        Добавление записи в поток Redis.

        :param name: название потока
        :param fields: поля записи
        :param maxlen: максимальная длина потока
        :param approximate: признак аппроксимации
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: идентификатор записи
        """
        try:
            logger.info(
                f"Добавление записи в поток Redis: name={name}, fields={fields}, "
                f"maxlen={maxlen}, approximate={approximate}",
            )

            async with Redis(connection_pool=self.redis_pool) as redis:
                stream_id = await redis.xadd(
                    name,
                    fields,
                    maxlen=maxlen,
                    approximate=approximate,
                )
                logger.info(f"Успешно добавлено в поток, id записи: {stream_id}")
                return stream_id
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка добавления записи в поток Redis: {exp}",
                exc_info=True,
            )
            raise

    async def xrange(
        self,
        name: str,
        count: Optional[int] = None,
    ) -> list[tuple[str, dict[bytes, bytes]]]:
        """
        Метод чтения записей из потока Redis.

        :param name: название потока
        :param count: количество записей
        :raises redis_exceptions.RedisError: Ошибка Redis.
        :return: записи из потока
        """
        try:
            async with Redis(connection_pool=self.redis_pool) as redis:
                return await redis.xrange(name, count=count)
        except redis_exceptions.RedisError as exp:
            logger.error(
                f"Ошибка возвращения записи из потока Redis: {exp}",
                exp_info=True,
            )
            raise

    async def set(
        self,
        key: str,
        value: Any,  # noqa: WPS110
        ex: int = settings.service_redis.default_ttl,
    ) -> None:
        """
        Сохранить значение по ключу в редис.

        Установлен дефолтный ex.

        :param key: key
        :param value: value
        :param ex: ex
        :return: None
        """
        return await super().set(key, value, ex)

    async def delete(self, key: str) -> int:
        """
        Удалить значение по ключу в редис.

        :param key: key
        :return: Количество удалённых ключей.
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            return await redis.delete(key)

    @asynccontextmanager
    async def client(self):
        """
        Redis client contextmanager.

        :yield: redis connection object
        """
        async with Redis(connection_pool=self.redis_pool) as redis:
            yield redis
