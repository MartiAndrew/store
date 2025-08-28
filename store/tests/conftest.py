from typing import AsyncGenerator, Generator

import pytest
from asgi_lifespan import LifespanManager
from fakeredis.aioredis import FakeRedis
from fastapi import FastAPI
from httpx import AsyncClient
from loguru import logger
from taskiq import InMemoryBroker, TaskiqState

from common.constance.tests.conftest import constance_close, constance_init
from common.service_db.tests.conftest import service_db_pool_close, service_db_pool_init
from common.service_redis.tests.conftest import service_redis_close, service_redis_init
from common.taskiq import broker
from common.token_cache.tests.conftest import token_cache_close, token_cache_init

from configuration import clients
from configuration.settings import Settings, settings
from store.web.application import get_app

services_mocks = {
    "service_db_pool": (service_db_pool_init, service_db_pool_close),
    "service_redis_pool": (service_redis_init, service_redis_close),
    "token_cache_redis_pool": (token_cache_init, token_cache_close),
    "constance_pool": (constance_init, constance_close),
}


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture()
async def fake_redis() -> AsyncGenerator[FakeRedis, None]:
    """
    Замокать редис.

    :yields: FakeRedis instance.
    """
    redis = FakeRedis(decode_responses=True)
    yield redis
    await redis.close()


@pytest.fixture
def service_settings() -> Generator[Settings, None, None]:
    """
    Замокать настройки сервиса.

    Это нужно для возможности разделения баз данных при запуске в несколько потоков
    for xdist.

    :yield: modifiable settings object.
    """
    saved = settings.model_copy(deep=True)

    yield settings

    settings.__setstate__(saved.__getstate__())  # noqa: WPS609


@pytest.fixture(scope="session")
async def top_session_scope_async_fixture() -> AsyncGenerator[None, None]:
    """
    Специальная корневая фикстура.

    Служит для фикса RuntimeError: event loop is closed.
    :yields: None.
    """
    yield


@pytest.fixture(scope="session")
async def mock_clients(worker_id):
    """
    Функция для мока сервисов.

    Функции init и close для мока сервисов в стейте.

    :yield: None
    """

    async def init():  # noqa: WPS430
        logger.info("mock_clients start")
        mocked_services = set(clients.WebClientsState.model_fields.keys())
        mocked_services |= set(clients.TaskiqClientsState.model_fields.keys())
        mocked_services |= set(clients.BaseWorkerClientsState.model_fields.keys())
        for service in mocked_services:  # type: ignore
            service_mock = services_mocks.get(service)
            if service_mock:
                service_init = service_mock[0]
                services[service] = await service_init(worker_id)
            else:
                raise Exception(f"Сервис {service} не замокан.")  # noqa: WPS454

    async def close():  # noqa: WPS430
        logger.info("mock_clients finish")
        for service, service_mock_data in services.items():
            service_mock = services_mocks.get(service)
            service_close = service_mock[1]
            await service_close(service_mock_data)

    services = {}
    await init()
    yield services
    await close()


@pytest.fixture(scope="function")
async def taskiq_state(
    mock_clients: None,
    monkeypatch,
) -> AsyncGenerator[TaskiqState, None]:
    """
    Стейт для taskiq.

    :yield: taskiq State
    """
    assert isinstance(broker.rabbit_broker, InMemoryBroker)
    await broker.rabbit_broker.startup()
    yield broker.rabbit_broker.state
    await broker.rabbit_broker.shutdown()


@pytest.fixture
async def fastapi_app() -> FastAPI:
    """
    Фикстура для создания FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    return get_app()


@pytest.fixture()
async def client(
    fastapi_app: FastAPI,
    mock_clients: None,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для создания клиента.

    :param fastapi_app: the application.
    :yields: client for the app.
    """
    async with LifespanManager(fastapi_app):
        async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
            yield ac
