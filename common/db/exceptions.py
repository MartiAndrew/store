from common.errors.error_responses import page_not_found
from common.errors.exceptions import ServiceError
from common.errors.schema import ErrorResponse


class FetchoneEmptyError(ServiceError):
    """Данные по запросу в БД не найдены."""

    response_data: ErrorResponse = page_not_found
