from importlib import metadata
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)
from pydantic_core import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles

from common.fastapi.middlewares import HeadersMiddleware
from common.locale.localization import get_locales
from common.logging.logging import LoggerMiddleware, init_logger
from common.sentry.sentry import init_sentry

from configuration.constants import SERVICE_NAME_LOWER
from store.web import lifetime
from store.web.api.router import api_router
from store.web.exception_handlers import validation_exception_handler

WEB_APP_ROOT = Path(__file__).parent


def init_app() -> FastAPI:
    """
    Инициализация и получение экземпляра приложения.

    Это основной конструктор приложения без startup.
    :return: экземпляр приложения.
    """
    app = FastAPI(
        title=SERVICE_NAME_LOWER,
        description=SERVICE_NAME_LOWER,
        version=metadata.version(SERVICE_NAME_LOWER),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    app.mount(
        "/static",
        StaticFiles(directory=WEB_APP_ROOT / "static"),
        name="static",
    )

    init_logger()
    init_sentry()

    app.include_router(router=api_router, prefix="/api")

    app.state.locales_gettext = get_locales()

    lifetime.register_startup_event(app)
    lifetime.register_shutdown_event(app)
    lifetime.register_exception_handler(app)
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        ValidationError,
        validation_exception_handler,  # type: ignore
    )

    return app


def get_app() -> FastAPI:
    """
    Получение экземпляра приложения.

    Это основной конструктор приложения.
    :return: экземпляр приложения.
    """
    app = init_app()

    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=HeadersMiddleware())
    app.add_middleware(CorrelationIdMiddleware, header_name="X-Request-ID")
    return app
