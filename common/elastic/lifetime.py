from elasticsearch import AsyncElasticsearch

from configuration.settings import settings


async def setup_elasticsearch() -> AsyncElasticsearch:
    """
    Создать клиент эластика.

    :return: Клиент эластика
    """
    return AsyncElasticsearch(hosts=settings.elasticsearch_url)


async def stop_elasticsearch(elastic_client: AsyncElasticsearch) -> None:
    """
    Закрыть клиент эластика.

    :param elastic_client: elastic_client
    """
    await elastic_client.close()
