import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture
from starlette import status

from configuration.settings import settings


@pytest.mark.anyio
async def test_version(
    mocker: MockerFixture,
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """Тестирует API с информацией по версии приложения."""
    mocker.patch.object(settings, "version", new="1.0")
    mocker.patch.object(settings, "commit_hash", new="")

    url = fastapi_app.url_path_for("version")
    response = await client.get(url)
    assert response.json() == {
        "version": "1.0",
        "commit_hash": "",
    }


@pytest.mark.anyio
async def test_health(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """Тестирует API, проверяющее состояние приложения."""
    url = fastapi_app.url_path_for("health_check")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_metrics(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """Тестирует получение метрик API."""
    url = fastapi_app.url_path_for("prometheus_metrics")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
