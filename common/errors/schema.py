import types
from typing import Any, Optional

from pydantic import BaseModel, field_validator
from starlette import status

DEFAULT_HEADERS = types.MappingProxyType(
    {
        "Content-Type": "application/json; charset=utf-8",
    },
)


class ErrResponseBody(BaseModel):
    """Тело ответа ошибки."""

    message: Optional[str]
    error_code: int
    verbose_message: Optional[str]
    extra: Optional[dict[str, Any]] = None

    def model_dump(  # type: ignore
        self,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Если extra не передано - не отдаём его в ответе.

        :param args: позиционные аргументы.
        :param kwargs: именованные аргументы
        :return: словарь
        """
        if self.extra is None:
            if kwargs.get("exclude") is None:
                kwargs["exclude"] = {"extra"}  # type: ignore
            else:
                kwargs["exclude"].add("extra")  # type: ignore
        return super().model_dump(*args, **kwargs)  # type: ignore


class ErrorResponse(BaseModel):
    """Модель http_client ответа-ошибки."""

    body: ErrResponseBody
    status_code: int = status.HTTP_400_BAD_REQUEST
    headers: dict[str, Any] = {}

    @field_validator("headers")
    def validate_headers(cls, headers: dict[str, Any]) -> dict[str, Any]:  # noqa: N805
        """
        Валидация headers.

        :param headers: headers
        :return: headers.
        """
        return {**DEFAULT_HEADERS, **headers}
