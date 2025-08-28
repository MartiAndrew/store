import abc
from typing import Any

from common.errors.error_responses import unknown_error, user_not_authorized
from common.errors.exceptions import ServiceError
from common.errors.schema import ErrorResponse


class TokenError(ServiceError, abc.ABC):
    """Ошибка токена."""

    response_data: ErrorResponse = unknown_error

    def __init__(self, *args: tuple[Any]):
        self.response_data.body.extra = self.extra

    @property
    @abc.abstractmethod
    def extra(self) -> dict[str, Any]:
        """Данные об ошибке."""


class InvalidTokenError(TokenError):
    """Базовый класс для ошибок токена авторизации."""

    def __init__(self, message: str, *args: tuple[Any]) -> None:
        self._message = message
        super().__init__(*args)

    @property
    def extra(self) -> dict[str, Any]:
        """Данные об ошибке.

        :return: расширенная информация об ошибке
        """
        return {
            "detail": "Given token not valid for any token type",
            "code": "token_not_valid",
            "messages": [
                {
                    "token_class": "AccessToken",
                    "token_type": "access",
                    "message": self._message,
                },
            ],
        }


class NotAccessTokenError(InvalidTokenError):
    """Передан неверный тип токена."""

    def __init__(self, *args: tuple[Any]) -> None:
        self._message = "Token has wrong type"
        super().__init__(self._message, *args)


class UserNotInTokensClaimsError(TokenError):
    """Передан токен с неизвестным пользователем."""

    @property
    def extra(self) -> dict[str, Any]:
        """Данные об ошибке.

        :return: расширенная информация об ошибке
        """
        return {
            "detail": "Token contained no recognizable user identification",
            "code": "token_not_valid",
        }


class TokensExpiredError(TokenError):
    """Токен просрочен."""

    @property
    def extra(self) -> dict[str, Any]:
        """Данные об ошибке.

        :return: расширенная информация об ошибке
        """
        return {
            "detail": "Missing or expired token.",
            "code": "token_not_valid",
        }


class UserNotAuthorizedError(ServiceError):
    """Пользователь не авторизован."""

    response_data: ErrorResponse = user_not_authorized
