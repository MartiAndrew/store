from redis import BusyLoadingError
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff

from configuration.settings import settings


async def setup_token_cache_redis() -> ConnectionPool:
    """
    Создать пул коннектов к редису кеша токенов.

    :return: Пул токен кеша
    """
    return ConnectionPool.from_url(
        str(settings.token_cache.redis_url),
        retry=Retry(
            ConstantBackoff(settings.token_cache.redis_number_retries_on_error),
            settings.token_cache.redis_number_retries_on_error,
        ),
        retry_on_error=[BusyLoadingError],
    )


async def stop_token_cache_redis(token_cache_redis_pool: ConnectionPool) -> None:
    """
    Закрыть пул коннектов к редису кеша токенов.

    :param token_cache_redis_pool: Пул токен кеша.
    """
    await token_cache_redis_pool.disconnect()
