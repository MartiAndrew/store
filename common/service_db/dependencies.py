from psycopg_pool import AsyncConnectionPool
from starlette.requests import Request


def get_service_db_pool(request: Request) -> AsyncConnectionPool:
    """
    Вернуть пул коннектов к БД сервиса.

    :param request: current request.
    :returns: database connections pool.
    """
    return request.app.state.clients.service_db_pool
