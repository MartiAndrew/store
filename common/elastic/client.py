from typing import Any

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from kino.services.elastic.dependencies import get_service_elasticsearch_client
from loguru import logger


class ElasticsearchClient:
    """ElasticsearchClient."""

    def __init__(
        self,
        elasticsearch_client: AsyncElasticsearch = Depends(
            get_service_elasticsearch_client,
        ),
    ):
        """
        Инициализировать ElasticsearchClient.

        :param elasticsearch_client: elasticsearch_client
        """
        self.client = elasticsearch_client

    async def search(
        self,
        index_name: str,
        query_text: str,
        size: str = 10,
    ) -> list[dict[Any, Any]]:
        """
        Поиск по индексу.

        :param index_name: index_name
        :param query_text: query_text
        :param size: кол-во записей в результате
        :return: Результат поиска
        """
        query = {
            "size": size,
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title"],
                    "fuzziness": "AUTO",
                },
            },
        }

        try:
            response = await self.client.search(index=index_name, body=query)
        except Exception as exc:
            logger.error(f"Запрос в Elasticsearch упал, причина: {exc}")
            return []

        return [hit["_source"] for hit in response["hits"]["hits"]]
