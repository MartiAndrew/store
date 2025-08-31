import sys

import psycopg_pool
from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from common.errors.exceptions import ServiceError
from common.locale.localization import locale_gettext
from common.logging.log_models import LogData
from common.taskiq.lifetime import setup_taskiq, stop_taskiq

from configuration.clients import WebClientsState
from configuration.settings import settings
from store import metrics


def register_startup_event(app: FastAPI) -> None:
    """
    Вызов функция для старта приложения.

    Настраивается телеметрия, клиенты и taskiq при необходимости.

    :param app: the fastAPI application.
    """

    async def _startup() -> None:  # noqa: WPS430
        web_clients_state: WebClientsState = await WebClientsState.clients_startup()
        app.state.clients = web_clients_state
        app.state.log_data = LogData(
            client_id="",
            request_id="",
            user="",
            device_id="",
        )
        await setup_taskiq()

    app.add_event_handler("startup", _startup)


def register_shutdown_event(app: FastAPI) -> None:
    """
    Выполняет действия, необходимые для завершения приложения.

    :param app: fastAPI application.
    """

    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.clients.clients_shutdown()
        await stop_taskiq()

    app.add_event_handler("shutdown", _shutdown)


def register_exception_handler(  # noqa: WPS231 C901
    app: FastAPI,
) -> None:
    """
    Регистрируем обработчик ошибок для ошибок ServiceError.

    :param app: fastAPI application.
    """

    @app.exception_handler(ServiceError)
    async def store_exception_handler(  # noqa: WPS430
        request: Request,
        exc: ServiceError,
    ) -> Response:
        """Обработка ошибок store_Exception.

        :param request: запрос от пользователя
        :param exc: ошибка возникшая во время обработки запроса
        :return: Response
        """
        body = exc.body.model_dump()
        gettext = locale_gettext(request)
        if body.get("message") and body.get("verbose_message"):
            body["message"] = gettext(body.get("message", ""))
            body["verbose_message"] = gettext(body.get("verbose_message", ""))

            if body.get("extra") and "parameter_name" in body["extra"]:
                body["message"] = body["message"].format(
                    parameter_name="".join(body["extra"]["parameter_name"]),
                )
                body["verbose_message"] = body["verbose_message"].format(
                    parameter_name="".join(body["extra"]["parameter_name"]),
                )
            if body.get("extra") and "msg" in body["extra"]:
                body["extra"]["msg"] = gettext(body["extra"]["msg"])

        return JSONResponse(
            jsonable_encoder(body),
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @app.exception_handler(psycopg_pool.PoolTimeout)
    async def db_pool_timeout_handler(  # noqa: WPS430
        request: Request,
        exc: psycopg_pool.PoolTimeout,
    ) -> Response:
        """Обработчик для учёта ошибок таймаута подключения к пулу БД.

        :param request: запрос от пользователя
        :param exc: ошибка возникшая во время обработки запроса
        :return: Response
        """
        metrics.db_pool_timeout_errors_count.inc()
        if settings.web.kill_pod_by_db_pool_timeout:
            errors_count = (
                metrics.db_pool_timeout_errors_count._value.get()  # noqa: WPS437
            )
            if settings.web.pool_timeout_errors_limit <= errors_count:
                logger.error(
                    f"Превышено кол-во ошибок таймаута при подключении к пулу БД. "
                    f"errors_count:{errors_count}, "
                    f"errors_limit: {settings.web.pool_timeout_errors_limit}.",
                )
                sys.exit(1)

        response = jsonable_encoder(
            {
                "verbose_message": "Internal Server Error",
                "error_code": 2,
                "message": "Internal Server Error",
            },
        )
        return JSONResponse(
            response,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
