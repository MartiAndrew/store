from fakeredis.aioredis import FakeRedis
from redis.asyncio import ConnectionPool

from configuration import clients


def get_token_cache_lifetime(redis: FakeRedis):
    """
    Получить функции для инициализации мока.

    :return: функции старта и завершения.
    """

    async def startup():  # noqa: WPS430
        return redis.connection_pool

    async def shutdown(_: ConnectionPool):  # noqa: WPS430
        await redis.flushall()

    return startup, shutdown


async def token_cache_init(
    _: str,
) -> FakeRedis:
    """
    Мок кеша токенов.

    :return: mocked redis.
    """
    redis = FakeRedis(decode_responses=True)

    token_cache_lifetime = get_token_cache_lifetime(redis)

    clients.CLIENTS_LIFETIME["token_cache_redis_pool"] = token_cache_lifetime

    return redis


async def token_cache_close(
    redis: FakeRedis,
) -> None:
    """Мок кеша токенов."""
    await redis.close()
