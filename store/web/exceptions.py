from starlette import status

from common.errors.exceptions import ServiceError
from common.errors.schema import ErrorResponse, ErrResponseBody

from store.web.error_responses import (  # noqa: WPS235
    PARAMS_VALIDATION_ERR_CODE,
    order_check_violation,
    order_not_found,
    user_not_authorized,
)


class UserNotAuthorizedError(ServiceError):
    """Пользователь не авторизован."""

    response_data: ErrorResponse = user_not_authorized


class OrderNotFoundError(ServiceError):
    """Заказ не найден."""

    response_data: ErrorResponse = order_not_found


class OrderCheckViolationError(ServiceError):
    """Ошибка консистентности продукта в заказе."""

    response_data: ErrorResponse = order_check_violation


class ParameterValidationError(ServiceError):
    """Несоответствие параметров условиям валидации."""

    def __init__(self, parameter_name: list[str] | str):
        self.response_data = ErrorResponse(
            body=ErrResponseBody(
                message="Значение не соответствует требованиям {parameter_name}.",
                error_code=PARAMS_VALIDATION_ERR_CODE,
                verbose_message="Значение не соответствует требованиям "
                "{parameter_name}.",
                extra={"parameter_name": [parameter_name]},
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
