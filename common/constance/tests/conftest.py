from fakeredis.aioredis import FakeRedis
from redis.asyncio import ConnectionPool

from configuration import clients


def get_constance_lifetime(redis: FakeRedis):
    """
    Получить функции для инициализации мока.

    :return: функции старта и завершения.
    """

    async def startup():  # noqa: WPS430
        return redis.connection_pool

    async def shutdown(_: ConnectionPool):  # noqa: WPS430
        await redis.flushall()

    return startup, shutdown


async def constance_init(
    _: str,
) -> FakeRedis:
    """
    Мок redis.

    :return: mocked redis.
    """
    redis = FakeRedis(decode_responses=True)

    constance_lifetime = get_constance_lifetime(redis)

    clients.CLIENTS_LIFETIME["constance_pool"] = constance_lifetime

    return redis


async def constance_close(
    redis: FakeRedis,
) -> None:
    """Мок redis."""
    await redis.close()
