import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

from loguru import logger
from psycopg import OperationalError
from psycopg_pool import PoolTimeout

PT = ParamSpec("PT")
RT = TypeVar("RT")
DECF = Callable[PT, Awaitable[RT]]


def db_command_retryer(  # noqa: WPS231, C901
    retries: int,
) -> Callable[[DECF], DECF]:
    """Фабрика декораторов.

    Принимает параметр retries, который означает сколько
    раз нужно повторить запрос при падении.

    :param retries: количество ретраев.

    :returns: decorator.
    """
    left_retries = {"retries": retries}

    def decorator(  # noqa: WPS231
        func: DECF,
    ) -> DECF:
        """
        Декоратор для функций, которые делают запрос к БД.

        :param func: оборачиваемая функция.

        :returns: inner.
        """

        @wraps(func)
        async def inner(  # noqa: WPS430
            *args: Any,
            **kwargs: Any,
        ) -> RT:
            """
            Добавляем ретраи для функции, которая делает запрос к БД.

            :param args: позиционные агрументы оборачиваемой функции.
            :param kwargs: именованные агрументы оборачиваемой функции.

            :raises OperationalError: если не получилось выпольнить запрос
                к базе и все ретраи исчерпаны.
            :raises PoolTimeout: если не получилось выпольнить запрос
                к базе из-за PoolTimeout и все ретраи исчерпаны.

            :returns: значения, которые возвращает оборачиваемся функция.
            """
            number_of_retries = 1
            timeout_exc = None

            while number_of_retries < left_retries["retries"] + 1:
                try:
                    logger.info(
                        f"Trying to execute {func.__name__}. "
                        f"Attempt - {number_of_retries}",
                    )
                    return await func(*args, **kwargs)  # type: ignore
                except (PoolTimeout, asyncio.TimeoutError) as t_exc:
                    logger.error(f"Can't execute {func.__name__} due to {t_exc}")
                    number_of_retries += left_retries["retries"] // 3
                    timeout_exc = t_exc
                except OperationalError as exc:
                    logger.error(f"Can't execute {func.__name__} due to {exc}")
                    number_of_retries += 1

            # если хотя бы один ретрай упал по таймауту, считаем что запрос упал
            # по таймауту
            if timeout_exc is not None:
                raise PoolTimeout("Max retries reached. Can't execute query")
            raise OperationalError("Max retries reached. Can't execute query")

        return inner  # type: ignore

    return decorator
