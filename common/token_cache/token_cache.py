from fastapi import Depends
from loguru import logger
from redis import exceptions as redis_exceptions
from redis.asyncio import ConnectionPool, Redis

from common.token_cache.dependencies import get_token_cache_redis_pool

from configuration.settings import settings


class TokenCacheService:
    """Сервис для работы с кешом токенов."""

    PREFIX: str = "ANTARES://jtis"

    def __init__(
        self,
        redis_pool: ConnectionPool = Depends(get_token_cache_redis_pool),
    ):
        self._redis_pool: ConnectionPool = redis_pool

    async def is_jwt_cached(self, jti: str) -> bool:
        """Проверка нализия jwt в кеше токенов.

        :param jti: jti пользователя
        :return: есть ли jti в кеше токенов
        """
        if settings.auth.token_cache_checking:
            profile_hex = ":".join([self.PREFIX, str(jti)])
            logger.info(f"Сформирован profile_hex: {profile_hex}")
            try:
                async with Redis(  # type: ignore
                    connection_pool=self._redis_pool,
                ) as redis:
                    cache = await redis.get(
                        profile_hex,
                    )
                    logger.info(f"Кеш токенов получен {cache!r}.")
            except redis_exceptions.ConnectionError as exp:
                logger.error(f"Ошибка подключения к кешу токенов {exp}.")
                return True
            return bool(cache)
        logger.info("Кеш токенов отключен.")
        return True
