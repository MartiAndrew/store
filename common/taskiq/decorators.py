import functools

from loguru import logger

from common.logging.log_models import LogData


def taskiq_logging(func):
    """
    Обогащает логгер данными из запроса.

    :param func: функция для дкеорирования
    :return: декоратор
    """

    @functools.wraps(func)
    async def wrapped(*args, log_data: LogData, **kwargs):  # noqa: WPS430
        with logger.contextualize(
            client_id=log_data.client_id,
            device_id=log_data.device_id,
            user=log_data.user,
            request_id=log_data.request_id,
        ):
            logger.info(f"Таска {func.__name__} стартовала")
            func_result = await func(*args, log_data=log_data, **kwargs)
            logger.info(f"Таска {func.__name__} завершилась")
        return func_result

    return wrapped
