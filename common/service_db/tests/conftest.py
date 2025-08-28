from pathlib import Path

from loguru import logger
from psycopg import sql
from psycopg_pool import AsyncConnectionPool

from common.service_db import migrator

from configuration import clients
from configuration.constants import SERVICE_NAME_LOWER, SERVICE_PATH
from configuration.settings import settings

SQL_CLEAR_TEST_DB_PATH = Path(
    f"{SERVICE_PATH}/db/service_db/sql/clear_testdb.sql",
)


async def drop_db() -> None:
    """Дропнуть тестовую БД после всех тестов."""
    logger.info("drop test db")
    async with AsyncConnectionPool(
        conninfo=str(settings.service_db.url.with_path("/postgres")),
    ) as pool:
        await pool.wait()
        async with pool.connection() as conn:
            await conn.set_autocommit(True)
            await conn.execute(
                "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                "FROM pg_stat_activity "
                "WHERE pg_stat_activity.datname = %(dbname)s "
                "AND pid <> pg_backend_pid();",
                params={
                    "dbname": settings.service_db.base_name,
                },
            )
            drop_db_query = "DROP DATABASE {0} ;"
            await conn.execute(
                sql.SQL(drop_db_query).format(
                    sql.Identifier(settings.service_db.base_name),
                ),
            )


async def create_db() -> None:
    """Создать тестовую БД."""
    logger.info("create test db")
    async with AsyncConnectionPool(
        conninfo=str(settings.service_db.url.with_path("/postgres")),
    ) as pool:
        await pool.wait()
        async with pool.connection() as conn_check:
            res = await conn_check.execute(
                "SELECT 1 FROM pg_database WHERE datname=%(dbname)s",
                params={
                    "dbname": settings.service_db.base_name,
                },
            )
            db_exists = False
            row = await res.fetchone()
            if row is not None:
                db_exists = row[0]

        if db_exists:
            await drop_db()

        async with pool.connection() as conn_create:
            await conn_create.set_autocommit(True)
            create_db_query = "CREATE DATABASE {0};"
            await conn_create.execute(
                sql.SQL(create_db_query).format(
                    sql.Identifier(settings.service_db.base_name),
                ),
            )


def get_service_db_lifetime(service_db_pool: AsyncConnectionPool):
    """
    Получить функции для инициализации мока.

    :return: функции старта и завершения.
    """

    async def startup():  # noqa: WPS430
        return service_db_pool

    async def shutdown(pool):  # noqa: WPS430
        async with pool.connection() as conn:
            await conn.execute(SQL_CLEAR_TEST_DB_PATH.read_text())

    return startup, shutdown


async def service_db_pool_init(
    worker_id: str,
) -> AsyncConnectionPool:
    """
    Мок service_db.

    :return: mocked pg pool.
    """
    db_base = f"{SERVICE_NAME_LOWER}_service_db_test_{worker_id}"
    settings.service_db.base_name = db_base
    await create_db()
    pool = AsyncConnectionPool(conninfo=str(settings.service_db.url), open=False)
    await pool.open(wait=True)

    migrator.func_upgrade(str(settings.service_db.url))

    service_db_lifetime = get_service_db_lifetime(pool)

    clients.CLIENTS_LIFETIME["service_db_pool"] = service_db_lifetime

    return pool


async def service_db_pool_close(pool: AsyncConnectionPool) -> None:
    """Мок service_db."""
    await pool.close()
    await drop_db()
