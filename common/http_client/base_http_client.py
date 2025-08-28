from typing import Type, TypeVar

from fastapi import Depends
from httpx import AsyncClient, Response
from loguru import logger
from pydantic import TypeAdapter, ValidationError

from common.http_client.dependencies import get_http_client

RT = TypeVar("RT")


class BaseAPIClient:
    """Базовый класс для запросов к различным сервисам."""

    def __init__(self, http_client: AsyncClient = Depends(get_http_client)):
        """
        Инициализация http_client клиента.

        :param http_client: http_client
        """
        self.http_client = http_client

    @staticmethod
    def validate_response(response: Response, response_model: Type[RT]) -> RT | None:
        """
        Валидируем пришедший response.

        Проверяем успешность ответа и
        пытаемся преобразовать его в json.

        :param response: ответ сервиса.
        :param response_model: Во что нужно конвертировать ответ

        :returns: Словарь с данными из ответа.
        """
        if not response.is_success:
            logger.error(f"Ответ ручки {response.url} не 20X из-за {response.text}")
            return None

        try:
            response_json = response.json()
        except ValueError:
            logger.error(f"Content-Type ответа не application/json в {response.url}")
            return None
        try:
            return TypeAdapter(response_model).validate_python(response_json)
        except ValidationError as exc:
            logger.error(
                f"Не получилось сконвертировать "
                f"ответ {response_json} от URL {response.url}"
                f" в {response_model}: {exc}",
            )
            return None
