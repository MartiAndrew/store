import asyncio
import traceback

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from common.db.retry import db_command_retryer

from configuration.settings import settings


async def check_db_connection(engine: AsyncEngine, timeout: float) -> None:
    """
    Проверяет подключение к базе данных при старте.
    :param engine: AsyncEngine
    """

    async def _check_connection():
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    await asyncio.wait_for(_check_connection(), timeout=timeout)


async def sqlalchemy_db_health(sqlalchemy_engine: AsyncEngine) -> dict[str, str]:
    """
    Проверка жизни для БД SQLAlchemy.

    :param sqlalchemy_engine: движок SQLAlchemy
    :return: errors
    """
    retryer = db_command_retryer(settings.sqlalchemy_db.command_retries)
    try:
        await retryer(check_db_connection)(
            sqlalchemy_engine,
            settings.sqlalchemy_db.connection_timeout,
        )
    except Exception as exc:
        logger.error(f"Проверка неуспешна {exc}: {traceback.format_exc()}")
        return {"Проверка подключения к sqlalchemy_db": str(exc)}
    return {}
