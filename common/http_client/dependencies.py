from httpx import AsyncClient
from starlette.requests import Request

from common.logging.log_models import LogData


def get_http_client(request: Request) -> AsyncClient:
    """
    Dependency которая возвращает httpx client с прокси-заголовками.

    :param request: данные запроса
    :return: httpx AsyncClient
    """
    proxy_headers = {}
    log_data: LogData = request.app.state.log_data
    proxy_headers.update(
        {
            "X-User-UUID": log_data.user,
            "X-Client-ID": log_data.client_id,
            "X-Request-ID": log_data.request_id,
            "X-Device-ID": log_data.device_id,
        },
    )
    if auth_header := request.headers.get("Authorization"):
        proxy_headers["Authorization"] = auth_header
    return AsyncClient(headers=proxy_headers)
