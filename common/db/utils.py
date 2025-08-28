from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from psycopg import AsyncClientCursor, AsyncCursor
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


@asynccontextmanager
async def cursor_manager(
    db_pool: AsyncConnectionPool,
    db_connection_timeout: Optional[float],
) -> AsyncGenerator[AsyncCursor[Any], None]:
    """
    Контекстный менеджер для получения курсора.

    :param db_pool: Postgres Pool.
    :param db_connection_timeout: Таймаут на коннект.
    :yields: курсор.
    """
    async with db_pool.connection(
        timeout=db_connection_timeout,
    ) as connection:
        async with AsyncClientCursor(
            connection=connection,
            row_factory=dict_row,
        ) as cursor:
            yield cursor


async def check_connection(
    db_pool: AsyncConnectionPool,
    db_connection_timeout: Optional[float],
) -> int:
    """
    Проверка коннекта к БД.

    :param db_pool: current request.
    :param db_connection_timeout: Таймаут на коннект.
    :raises ValueError: если результат запроса не совпадает с ожиданиями
    :returns: [{"?column?":1,}]
    """
    async with cursor_manager(
        db_pool=db_pool,
        db_connection_timeout=db_connection_timeout,
    ) as cursor:
        await cursor.execute("SELECT 1 as res")
        fetch = await cursor.fetchone()
        if not fetch or fetch["res"] != 1:
            raise ValueError("ping postgres invalid value")
        return fetch["res"]
