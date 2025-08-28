from redis import BusyLoadingError
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff

from configuration.settings import settings


async def setup_service_redis() -> ConnectionPool:
    """
    Создать пул коннектов к редис.

    :return: пул коннектов к редис.
    """
    return ConnectionPool.from_url(
        str(settings.service_redis.url),
        retry=Retry(
            ConstantBackoff(settings.service_redis.number_retries_on_error),
            settings.service_redis.number_retries_on_error,
        ),
        retry_on_error=[BusyLoadingError],
    )


async def stop_service_redis(service_redis_pool: ConnectionPool) -> None:
    """
    Закрыть пул коннектов к редис.

    :param service_redis_pool: пул коннектов к редис.
    """
    await service_redis_pool.disconnect()
