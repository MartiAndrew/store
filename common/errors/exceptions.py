import abc
from typing import Any

from common.errors.error_responses import (
    invalid_uuid,
    page_not_found,
    user_not_authorized,
)
from common.errors.schema import ErrorResponse, ErrResponseBody


class ServiceError(Exception, abc.ABC):
    """Базовая HTTP ошибка."""

    response_data: ErrorResponse

    @property
    def headers(self) -> dict[str, Any]:
        """Заголовки ответа.

        :return: заголовки ответа
        """
        return self.response_data.headers

    @property
    def body(self) -> ErrResponseBody:
        """Тело ответа.

        :return: тело ответа
        """
        return self.response_data.body

    @property
    def status_code(self) -> int:
        """Код ответа.

        :return: код ответа
        """
        return self.response_data.status_code


class PageNotFoundError(ServiceError):
    """Страница не найдена."""

    response_data: ErrorResponse = page_not_found


class InvalidUuidError(ServiceError):
    """Некорректный UUID."""

    response_data: ErrorResponse = invalid_uuid


class UserNotAuthorizedError(ServiceError):
    """Пользователь не авторизован."""

    response_data: ErrorResponse = user_not_authorized


class CustomUnicodeDecodeError(UnicodeDecodeError):
    """Кастомный UnicodeDecodeError."""

    def __init__(self, obj, *args):  # noqa: WPS110
        self.obj = obj  # noqa: WPS110
        super().__init__(*args)

    def __str__(self):
        return "{0}. You passed in {1} ({2})".format(
            super().__str__(),
            self.obj,
            type(self.obj),
        )
