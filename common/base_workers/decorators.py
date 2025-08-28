import functools
import uuid

from loguru import logger


def message_logging(func):
    """
    Обогащает логгер данными из запроса.

    :param func: функция для декорирования
    :return: декоратор
    """

    @functools.wraps(func)
    async def wrapped(*args, **kwargs):  # noqa: WPS430
        with logger.contextualize(
            request_id=uuid.uuid4().hex,
        ):
            func_result = await func(*args, **kwargs)
        return func_result

    return wrapped
