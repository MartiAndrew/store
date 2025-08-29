from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request

from common.locale.localization import locale_gettext

from store.web.error_responses import (
    PARAMS_MISSING_ERR_CODE,
    PARAMS_VALIDATION_ERR_CODE,
)
from store.web.errors import (
    FloatValidationError,
    IntegerValidationError,
    ListValidationError,
    NonNegativeIntValidationError,
    StringValidationError,
    UuidValidationError,
)

custom_type_validation_mapping = {
    "float_parsing": FloatValidationError,
    "float_type": FloatValidationError,
    "int_parsing": IntegerValidationError,
    "int_type": IntegerValidationError,
    "uuid_parsing": UuidValidationError,
    "uuid_type": UuidValidationError,
    "string_type": StringValidationError,
    "greater_than": NonNegativeIntValidationError,
    "list_type": ListValidationError,
}

string_validation_error = {
    "string_too_long",
    "string_too_short",
    "string_pattern_mismatch",
    "string_invalid",
    "string_regex_error",
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
    gettext = locale_gettext(request)

    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": gettext("Недопустимое значение."),
            "error_code": PARAMS_VALIDATION_ERR_CODE,
            "verbose_message": gettext("Недопустимое значение."),
            "extra": jsonable_encoder(exc.errors()),
        },
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
    gettext = locale_gettext(request)

    missing_fields = [
        error["loc"][-1]
        for error in exc.errors()  # noqa: WPS361
        if error["type"] == "missing"
    ]

    if missing_fields:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": gettext(
                    "Отсутствуют обязательные параметры: {fields}.",
                ).format(fields=", ".join(missing_fields)),
                "error_code": PARAMS_MISSING_ERR_CODE,
                "verbose_message": gettext(
                    "Отсутствуют обязательные параметры: {fields}.",
                ).format(fields=", ".join(missing_fields)),
            },
        )

    invalid_fields = [
        error["loc"][-1]
        for error in exc.errors()
        if error["type"] in string_validation_error
    ]

    if invalid_fields:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": gettext(
                    "Значение не соответствует требованиям {parameter_name}.",
                ).format(parameter_name=", ".join(invalid_fields)),
                "error_code": PARAMS_VALIDATION_ERR_CODE,
                "verbose_message": gettext(
                    "Значение не соответствует требованиям {parameter_name}.",
                ).format(parameter_name=", ".join(invalid_fields)),
                "extra": {"parameter_name": invalid_fields},
            },
        )

    error_json = exc.errors()[0]

    error_handler = custom_type_validation_mapping.get(error_json["type"])
    if error_handler:
        return error_handler(request, error_json).response

    return await default_request_validation_exception_handler(request, exc)
