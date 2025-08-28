from fastapi import Depends
from psycopg import AsyncCursor
from psycopg_pool import AsyncConnectionPool

from common.db.base_queries import BaseQuery
from common.service_db.dependencies import get_service_db_pool

from configuration.settings import settings


class BaseServiceDbQuery(BaseQuery):
    """Базовый класс для всех запросов в service_db."""

    def __init__(  # noqa: WPS612
        self,
        db: AsyncConnectionPool | AsyncCursor = Depends(get_service_db_pool),
    ):
        """
        Иницилизация базового класса.

        :param db: пул соединений с базой или открытый курсор.
        """
        super().__init__(db, settings.service_db.connection_timeout)
