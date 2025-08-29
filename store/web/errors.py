from typing import Any, Dict, Union

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from common.locale.localization import locale_gettext


class BaseValidationError(Exception):
    """Базовый класс для ошибок валидации."""

    error_code = 0
    message = ""

    def __init__(
        self,
        request: Request,
        error_json: Any,
        *message_args: Any,
        **message_kwargs: Any,
    ) -> None:
        """Инициализация.

        :param request: Объект запроса.
        :param error_json: JSON с базовой ошибкой валидации.
        :param message_args: Позиционные параметры для сообщения об ошибке.
        :param message_kwargs: Именованные параметры для сообщения об ошибке.
        """
        self.request = request
        self.error_json = error_json
        super().__init__(self.message)

    def get_body(self) -> Dict[str, Union[str, int]]:
        """Детали ошибки.

        :returns: Возвращаемые ошибки.
        """
        gettext = locale_gettext(self.request)
        return {
            "message": gettext(self.message),
            "error_code": self.error_code,
            "verbose_message": gettext(self.message),
        }

    @property
    def response(self) -> ORJSONResponse:
        """Отформатированный JSON-ответ ошибки валидации.

        :returns: ответ с ошибкой.
        """
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                self.get_body(),
            ),
        )


class FloatValidationError(BaseValidationError):
    """Ошибка валидации поля с float числом."""

    message = "Недопустимое значение Float."
    error_code = 3


class IntegerValidationError(BaseValidationError):
    """Ошибка валидации поля с int числом."""

    message = "Недопустимое значение Integer."
    error_code = 3


class UuidValidationError(BaseValidationError):
    """Ошибка валидации UUID поля."""

    message = "Недопустимое значение UUID."
    error_code = 3


class StringValidationError(BaseValidationError):
    """Ошибка валидации строки."""

    message = "Недопустимое значение String."
    error_code = 3


class NonNegativeIntValidationError(BaseValidationError):
    """Ошибка валидации NonNegativeInt."""

    message = "Недопустимое значение NonNegativeInt."
    error_code = 3


class ListValidationError(BaseValidationError):
    """Ошибка валидации строки."""

    message = "Недопустимое значение List."
    error_code = 3
