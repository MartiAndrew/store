from redis.asyncio import ConnectionPool
from starlette.requests import Request


def get_token_cache_redis_pool(request: Request) -> ConnectionPool:
    """
    Вернуть пул коннектов к кешу токенов.

    :param request: current request.
    :returns: redis connections pool.
    """
    return request.app.state.clients.token_cache_redis_pool
