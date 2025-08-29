import asyncio
from typing import Any, Coroutine, Self, TypeVar

import psycopg_pool
from loguru import logger
from pydantic import BaseModel, ConfigDict
from redis.asyncio import ConnectionPool

from common.constance.lifetime import setup_constance, stop_constance
from common.elastic.lifetime import setup_elasticsearch, stop_elasticsearch
from common.rabbitmq.lifetime import setup_rabbit, stop_rabbit
from common.service_db.lifetime import setup_service_db, stop_service_db
from common.service_db.service_db_health import service_db_health
from common.service_redis.lifetime import setup_service_redis, stop_service_redis
from common.sqlalchemy.lifetime import close_engine, setup_sqlalchemy_engine
from common.token_cache.lifetime import setup_token_cache_redis, stop_token_cache_redis

ClientState = TypeVar("ClientState")
ServiceHealthFunc = Coroutine[Any, Any, dict[str, str]]
CLIENTS_LIFETIME = {  # noqa: WPS407 - мутабельность нужна для моков
    "service_db_pool": (setup_service_db, stop_service_db),
    "service_redis_pool": (setup_service_redis, stop_service_redis),
    "token_cache_redis_pool": (setup_token_cache_redis, stop_token_cache_redis),
    "constance_pool": (setup_constance, stop_constance),
    "rabbitmq_connection": (setup_rabbit, stop_rabbit),
    "sqlalchemy_engine": (setup_sqlalchemy_engine, close_engine),
    "elasticsearch": (setup_elasticsearch, stop_elasticsearch),
}


class BaseClientState(BaseModel):
    """
    Базовая модель хранения клиентов и их подключения.

    Модель клиентов используется для того, чтобы был удобный startup|shutdown.
    Также в web, taskiq, workers эти клиенты подключаются в state.
    Поэтому коннект к клиенту получать достаточно легко.
    - request.app.state.clients в web
    - state.clients в taskiq
    - Параметр функции process в Воркерах
    Список возможных клиентов из common части можно посмотреть в CLIENTS_LIFETIME.
    Для подклчюения клиента из common можно воспользоваться генератороа
    python ./gen/generate.py connect <service_name>
    Он автоматически добавится в Настройки и клиенты для Web и taskiq.
    В воркерах придется подключать руками.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    async def clients_startup(
        cls,
    ) -> Self:
        """
        Инициализация клиентов.

        :return: объект с подключенными клиентами.
        """
        client_state_init_params: dict[str, Any] = {}
        for client in cls.model_fields.keys():  # type: ignore
            client_lifetime = CLIENTS_LIFETIME.get(client)
            if client_lifetime:
                client_startup = client_lifetime[0]
                client_obj = await client_startup()
                logger.info(f"Подключили клиент {client}: {client_obj}")
                client_state_init_params[client] = client_obj
        return cls(**client_state_init_params)

    async def clients_shutdown(
        self,
    ):
        """Остановка клиентов."""
        for client in self.model_fields.keys():  # type: ignore
            client_lifetime = CLIENTS_LIFETIME.get(client)
            if client_lifetime:
                client_shutdown = client_lifetime[1]
                await client_shutdown(  # type: ignore
                    getattr(self, client),
                )

    def get_funcs_for_health_check(self) -> list[ServiceHealthFunc]:
        """
        Возвращает функции для проверки в health.

        :return: Список функций.
        """
        return []

    async def health(self) -> dict[str, str]:
        """
        Возвращает health-статус.

        :return: Словарь ошибок (пустой в случае, если все хорошо).
        """
        errors_services = await asyncio.gather(
            *self.get_funcs_for_health_check(),
        )
        errors = {}
        for errors_service in errors_services:
            errors.update(errors_service)
        return errors


class WebClientsState(BaseClientState):
    """Класс для хранения подключенных клиентов в web lifetime."""

    # Не удалять строчку, по ней идет поиск
    service_db_pool: psycopg_pool.AsyncConnectionPool

    def get_funcs_for_health_check(self):
        """
        Возвращает функции для проверки в health.

        Примеры подключений:
        ```
        return [service_db_health(self.service_db_pool)]
        ```

        :return: Список функций.
        """
        return [service_db_health(self.service_db_pool)]


class TaskiqClientsState(BaseClientState):
    """Класс для хранения подключенных клиентов в taskiq lifetime."""

    # Не удалять строчку, по ней идет поиск
    token_cache_redis_pool: ConnectionPool

    def get_funcs_for_health_check(self):
        """
        Возвращает функции для проверки в health.

        :return: Список функций.
        """
        return []


class BaseWorkerClientsState(BaseClientState):
    """Класс для хранения подключенных клиентов в worker lifetime."""
