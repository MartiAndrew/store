from typing import Any

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse


class BaseResponse(JSONResponse):
    """A class for generating an http_client response."""

    def __init__(
        self,
        content_object: BaseModel | None = None,
        status_code: int = status.HTTP_200_OK,
        headers: dict[str, Any] | None = None,
    ) -> None:
        """
        Initializing the object.

        :param content_object: paidantic object (handle response)
        :param status_code: response code
        :param headers: headers
        """
        try:
            content_object = jsonable_encoder(
                content_object,
            )
        except (TypeError, ValueError) as exc:
            logger.error(
                f"Не удалось сериализовать данные в JSON: {exc}",
                exc_info=True,
            )
        default_headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        if headers:
            default_headers.update(headers)
        super().__init__(
            content=content_object or {},
            headers=default_headers,
            status_code=status_code,
        )
