import traceback

from loguru import logger
from psycopg_pool import AsyncConnectionPool

from common.db.retry import db_command_retryer
from common.db.utils import check_connection

from configuration.settings import settings


async def service_db_health(service_db_pool: AsyncConnectionPool) -> dict[str, str]:
    """
    Проверка жизни для сервисной БД.

    :param service_db_pool: Пул коннектов к БД
    :return: errors
    """
    retryer = db_command_retryer(settings.service_db.command_retries)
    try:
        await retryer(check_connection)(
            service_db_pool,
            settings.service_db.connection_timeout,
        )
    except Exception as exc:
        logger.error(f"Проверка неуспешна {exc}: {traceback.format_exc()}")
        return {"Проверка подключения к service_db": str(exc)}
    return {}
