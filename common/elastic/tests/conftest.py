from unittest.mock import AsyncMock

from elasticsearch import AsyncElasticsearch

from configuration import clients


async def elasticsearch_init(
    _: str,
) -> AsyncMock:
    """
    Мок  elasticsearch.

    :returns: мок.
    """
    mock = AsyncMock(spec=AsyncElasticsearch)
    clients.CLIENTS_LIFETIME["elasticsearch"] = [mock, mock]
    return mock


async def elasticsearch_close(_: None) -> None:
    """Мок  elasticsearch."""
