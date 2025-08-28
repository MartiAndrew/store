from redis.asyncio import ConnectionPool
from starlette.requests import Request


def get_service_redis_pool(request: Request) -> ConnectionPool:
    """
    Вернуть пул коннектов к редис.

    :param request: current request.
    :returns: redis connections pool.
    """
    return request.app.state.clients.service_redis_pool
