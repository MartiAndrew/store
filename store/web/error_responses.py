from starlette import status

from common.errors.schema import ErrorResponse, ErrResponseBody

PARAMS_VALIDATION_ERR_CODE = 6
PARAMS_MISSING_ERR_CODE = 7
PARAMS_NOT_FOUND_ERR_CODE = 4
PARAMS_CHECK_VIOLATION_ERR_CODE = 5

order_not_found = ErrorResponse(
    body=ErrResponseBody(
        message="Заказ не найден.",
        error_code=PARAMS_NOT_FOUND_ERR_CODE,
        verbose_message="Заказ не найден.",
    ),
    status_code=status.HTTP_404_NOT_FOUND,
)

order_check_violation = ErrorResponse(
    body=ErrResponseBody(
        message="Недостаточное количество товара.",
        error_code=PARAMS_CHECK_VIOLATION_ERR_CODE,
        verbose_message="Недостаточное количество товара.",
    ),
    status_code=status.HTTP_409_CONFLICT,
)
