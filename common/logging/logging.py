import logging
import re
import sys
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

import jwt
import stackprinter
from asgi_correlation_id.context import correlation_id
from loguru import logger
from opentelemetry.trace import INVALID_SPAN, INVALID_SPAN_CONTEXT, get_current_span
from starlette.datastructures import Headers
from yarl import URL

from common.auth.user import device_id_from_header
from common.logging.log_models import LogData

from configuration.constants import NO_LOG_URLS
from configuration.settings import settings

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send


DEVICE_REGEX = re.compile(r"deviceID\s*:\s+(?P<device_id>.+)\sN")


class InterceptHandler(logging.Handler):
    """Перехватчик стандартных логов."""

    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        """
        Перехват дефолтных логов.

        :param record: запись в лог.
        """
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def _get_log_format(record):
    msg_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| {level} "
        "| {name} "
        "| {extra[client_id]} "
        "| {extra[device_id]} "
        "| {extra[user]} "
        "| {extra[request_id]} "
        "| <cyan>({file}).{function}({line})</cyan> "
        "| <level>{message}</level>"
    )
    if record["exception"] is None:
        record["extra"]["stack"] = ""
    else:
        record["extra"]["stack"] = stackprinter.format(record["exception"])
    if settings.logging.log_in_one_line:
        stack = record["extra"]["stack"].replace("\n", "\\n")  # noqa: WPS342
        record["extra"]["stack"] = stack
        record["message"] = record["message"].replace("\n", "\\n")  # noqa: WPS342
        msg_format = f"{msg_format} {{extra[stack]}}\n"
    else:
        msg_format = f"{msg_format} {{exception}}\n"

    span = get_current_span()
    record["extra"]["span_id"] = 0
    record["extra"]["trace_id"] = 0
    if span != INVALID_SPAN:
        span_context = span.get_span_context()
        if span_context != INVALID_SPAN_CONTEXT:
            record["extra"]["span_id"] = format(span_context.span_id, "016x")
            record["extra"]["trace_id"] = format(span_context.trace_id, "032x")

    return msg_format


def _get_handler_filter_db_echo(record) -> bool:
    if settings.logging.db_echo:
        return True
    return "Сформирован SQL запрос" not in record["message"]


def init_logger() -> None:
    """Инициализирует логгер с заданным уровнем."""
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=settings.logging.lib_log_level.value,
    )

    # set logs output, level and format
    logger.remove()

    logger.configure(
        extra={
            "client_id": "",
            "device_id": "",
            "user": "",
            "request_id": "",
        },
    )
    logger.add(
        sys.stdout,
        level=settings.logging.log_level.value,
        colorize=True,
        enqueue=True,
        format=_get_log_format,
        filter=_get_handler_filter_db_echo,
    )
    if settings.logging.lib_log_level != settings.logging.log_level:
        logger.warning("Уровень логов приложения и библиотек не совпадает.")


@dataclass
class LoggerMiddleware:
    """Миддлваря для добавления в логи extra."""

    app: "ASGIApp"
    client_header_name: str = "X-Client-ID"
    user_agent_header_name: str = "User-Agent"

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Миддлваря. Добавляет в логгер extra переменные.

        :param scope: Наследованный параметр миддлвари
        :param receive: Наследованный параметр миддлвари
        :param send: Наследованный параметр миддлвари
        """
        if scope.get("path") in NO_LOG_URLS:
            await self.app(scope, receive, send)
            return

        if scope["type"] != "http_client":
            await self.app(scope, receive, send)
            return

        log = logger.patch(
            lambda record: record.update(name="request-response"),  # type: ignore
        )
        headers = Headers(scope=scope)

        device_id = device_id_from_header(
            headers.get(self.user_agent_header_name.lower(), ""),
        )
        device_id = device_id or headers.get("X-Device-ID", "")
        user = self._get_user_uuid_from_auth_header(
            headers.get("Authorization", ""),
        )
        user = user or headers.get("X-User-UUID", "")

        log_data = LogData(
            client_id=headers.get(self.client_header_name.lower(), ""),
            device_id=device_id,
            user=user,
            request_id=correlation_id.get() or "",
        )
        scope["app"].state.log_data = log_data

        with log.contextualize(
            client_id=log_data.client_id,
            device_id=log_data.device_id,
            user=log_data.user,
            request_id=log_data.request_id,
        ):
            await self._run_contextualize_app(scope, receive, send, log)

    async def _run_contextualize_app(
        self,
        scope: "Scope",
        receive: "Receive",
        send: "Send",
        log,
    ) -> None:
        """
        Вызов дальнейшего процесса обработки ручки с контекстом в логе.

        :param scope: Наследованный параметр миддлвари
        :param receive: Наследованный параметр миддлвари
        :param send: Наследованный параметр миддлвари
        :param log: логгер с пропатченным именем.

        :raises BaseException: Отлов и прокидывание исключения из запроса.
        """

        async def handle_outgoing_request(message: "Message") -> None:  # noqa: WPS430
            msg_type = message["type"]
            if msg_type == "http_client.response.start":
                log.info(
                    "Ответ {0} {1} Статус {2}".format(
                        scope.get("method"),
                        URL.build(
                            path=scope.get("path", ""),
                            query_string=scope.get("query_string", "").decode("utf-8"),
                        ).human_repr(),
                        message.get("status"),
                    ),
                )
            if (
                msg_type == "http_client.response.body"
                and settings.logging.echo_response_body
            ):
                log.info(
                    "Тело ответа {0} {1} -- {2}".format(
                        scope.get("method"),
                        URL.build(
                            path=scope.get("path", ""),
                            query_string=scope.get("query_string", "").decode("utf-8"),
                        ).human_repr(),
                        message.get("body", "").decode(),
                    ),
                )

            await send(message)

        log.info(
            "Запрос {0} {1} {2}".format(
                scope.get("method"),
                URL.build(
                    path=scope.get("path", ""),
                    query_string=scope.get("query_string", "").decode("utf-8"),
                ).human_repr(),
                scope.get("headers"),
            ),
        )
        try:
            await self.app(scope, receive, handle_outgoing_request)
        except BaseException:  # noqa: WPS424
            logger.error(
                "Ответ {0} {1} Статус 500".format(
                    scope.get("method"),
                    URL.build(
                        path=scope.get("path", ""),
                        query_string=scope.get("query_string", "").decode("utf-8"),
                    ).human_repr(),
                ),
            )
            raise

    @staticmethod
    def _get_payload(auth) -> dict[str, str]:
        try:
            return jwt.decode(
                auth.replace("Bearer ", "", 1),
                key=settings.auth.jwt_signing_key,
                algorithms=["HS256", "HS384", "HS512"],
            )
        except jwt.PyJWTError:
            return {}

    def _get_user_uuid_from_auth_header(self, auth: str) -> str:
        """
        Получить id пользователя из токена авторизации.

        :param auth: токен авторизации
        :return: UUID пользователя
        """
        if not auth:
            return ""
        payload = self._get_payload(auth)
        if not payload:
            return ""
        raw_user_uuid = payload.get("uuid", "")
        try:
            return uuid.UUID(raw_user_uuid).hex
        except ValueError:
            return ""
