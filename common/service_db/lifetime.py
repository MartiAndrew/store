import os

import psycopg_pool

from common.db.base_queries import PrepareAsyncConnection

from configuration.settings import settings


async def setup_service_db() -> psycopg_pool.AsyncConnectionPool:
    """
    Создать пул коннектов к БД сервиса.

    :return: Пул коннектов к БД проекта.
    """
    service_db_pool = psycopg_pool.AsyncConnectionPool(
        conninfo=str(settings.service_db.url),
        connection_class=PrepareAsyncConnection,
        min_size=settings.service_db.pool_min_size,
        max_size=settings.service_db.pool_max_size,
        max_lifetime=settings.service_db.pool_max_lifetime,
        kwargs={"application_name": os.uname()[1]},
        open=False,
    )
    await service_db_pool.open(wait=True)
    return service_db_pool


async def stop_service_db(service_db_pool: psycopg_pool.AsyncConnectionPool) -> None:
    """
    Закрыть пул коннектов к БД сервиса.

    :param service_db_pool: Пул коннектов к БД проекта.
    """
    await service_db_pool.close()
