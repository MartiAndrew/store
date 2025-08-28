from starlette import status

from common.errors.schema import ErrorResponse, ErrResponseBody

PAGE_NOT_FOUND_ERR_CODE = 1
UNKNOWN_ERR_CODE = 1
INVALID_UUID_ERR_CODE = 18


page_not_found = ErrorResponse(
    body=ErrResponseBody(
        message="Страница не найдена.",
        error_code=PAGE_NOT_FOUND_ERR_CODE,
        verbose_message="Страница не найдена.",
    ),
    status_code=status.HTTP_404_NOT_FOUND,
)


invalid_uuid = ErrorResponse(
    body=ErrResponseBody(
        message="Некорректное значение UUID.",
        error_code=INVALID_UUID_ERR_CODE,
        verbose_message="Некорректное значение UUID.",
    ),
    status_code=status.HTTP_400_BAD_REQUEST,
)


unknown_error = ErrorResponse(
    body=ErrResponseBody(
        message="Что-то пошло не так.",
        error_code=UNKNOWN_ERR_CODE,
        verbose_message="Что-то пошло не так.",
    ),
    status_code=status.HTTP_401_UNAUTHORIZED,
    headers={
        "WWW-Authenticate": 'Bearer realm="api"',
        "Allow": "GET, HEAD, OPTIONS",
        "Vary": "Accept, Accept-Language, Cookie",
    },
)


user_not_authorized = ErrorResponse(
    body=ErrResponseBody(
        message="Учетные данные не были предоставлены.",
        error_code=1,
        verbose_message="Учетные данные не были предоставлены.",
    ),
    status_code=status.HTTP_401_UNAUTHORIZED,
)
