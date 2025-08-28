from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request

from store.web.errors import (
    FloatValidationError,
    IntegerValidationError,
    UploadfileValidationError,
    UuidValidationError,
)

custom_validation_mapping = {
    "float_parsing": FloatValidationError,
    "int_parsing": IntegerValidationError,
    "uuid_parsing": UuidValidationError,
    "missing": UploadfileValidationError,
}


async def default_request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> ORJSONResponse:
    """
    Стандартный обработчик ошибок валидации.

    :param request: Объект запроса.
    :param exc: Тип исключения ошибки валидации.
    :return: форматированный JSON с ошибкой валидации.
    """
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())},
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> ORJSONResponse:
    """
    Обработчик ошибок валидации.

    :param request: данные запроса.
    :param exc: класс ошибки валидации.
    :return: форматированный JSON-ответ с кодом ошибки и сообщением.
    """
    error_json = exc.errors()[0]

    error_handler = custom_validation_mapping.get(error_json["type"])
    if error_handler:
        return error_handler(request, error_json).response

    return await default_request_validation_exception_handler(request, exc)
