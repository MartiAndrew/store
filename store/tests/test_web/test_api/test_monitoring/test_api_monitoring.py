import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


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
