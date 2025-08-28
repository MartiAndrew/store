from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from loguru import logger
from psycopg import AsyncConnection, AsyncCursor
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel
from typing_extensions import Self


class PrepareAsyncConnection(AsyncConnection):  # type: ignore
    """Async connection для transaction mode."""

    @classmethod
    async def connect(cls, conninfo: str = "", **kwargs: Any) -> Self:
        """Connect with prepare_threshold=0.

        :param conninfo: connection info.
        :param kwargs: keyword arguments.
        :return: self.
        """
        return await super().connect(conninfo, prepare_threshold=None, **kwargs)


class BaseQuery:
    """Базовый класс для всех запросов."""

    def __init__(
        self,
        db: AsyncConnectionPool | AsyncCursor,
        timeout: float | None = None,
    ):
        """
        Иницилизация базового класса.

        :param db: пул соединений с базой или открытый курсор.
        :param timeout: timeout на получение коннекта.
        """
        self.db: AsyncConnectionPool | AsyncCursor = db
        self.timeout = timeout
        self.query_log = logger.patch(
            lambda record: record.update(name="query-printer"),  # type: ignore
        )

    @asynccontextmanager
    async def cursor(
        self,
        binary: bool = True,
        autocommit: bool | None = None,
    ) -> AsyncGenerator[AsyncCursor[Any], None]:
        """
        Контекстный менеджер для получения курсора.

        :param binary: Указывает на формат возвращаемых данных.
        :param autocommit: Если передан bool, то установит autocommit.
            Если передан None, set_autocommit не вызовется.
        :yields: курсор.
        """
        if isinstance(self.db, AsyncConnectionPool):
            async with self.db.connection(
                timeout=self.timeout,
            ) as connection:
                if autocommit is not None:
                    await connection.set_autocommit(autocommit)
                async with connection.cursor(
                    binary=binary,
                    row_factory=dict_row,
                ) as cursor:
                    yield cursor
        else:
            yield self.db


class BaseTestQuery(BaseQuery):
    """Базовый класс для тестовых запросов."""

    async def _create_model(self, query: str, schema_instance: BaseModel) -> None:
        """
        Метод для выполнения запросов в тестовую БД.

        :param schema_instance: инстанс схемы данных.
        :param query: запрос для создания.
        """
        async with self.cursor() as cursor:
            await cursor.execute(
                query,
                schema_instance.model_dump(),
            )
