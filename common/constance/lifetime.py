from redis import BusyLoadingError
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff

from configuration.settings import settings


async def setup_constance() -> ConnectionPool:
    """
    Создать пул коннектов к redis.

    :return: пул коннектов к редис.
    """
    return ConnectionPool.from_url(
        str(settings.constance.url),
        retry=Retry(
            ConstantBackoff(settings.constance.number_retries_on_error),
            settings.constance.number_retries_on_error,
        ),
        retry_on_error=[BusyLoadingError],
    )


async def stop_constance(constance_pool: ConnectionPool) -> None:
    """
    Закрыть пул коннектов к redis.

    :param constance_pool: пул коннектов к редис.
    """
    await constance_pool.disconnect()
