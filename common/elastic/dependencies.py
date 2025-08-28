from elasticsearch import AsyncElasticsearch
from starlette.requests import Request


def get_service_elasticsearch_client(request: Request) -> AsyncElasticsearch:
    """
    Вернуть elasticsearch клиент.

    :param request: current request.
    :returns: elasticsearch клиент.
    """
    return request.app.state.clients.elasticsearch
