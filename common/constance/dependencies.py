from redis.asyncio import ConnectionPool
from starlette.requests import Request


def get_constance_pool(request: Request) -> ConnectionPool:
    """
    Вернуть пул коннектов к redis.

    :param request: current request.
    :returns: redis connections pool.
    """
    return request.app.state.clients.constance_pool
