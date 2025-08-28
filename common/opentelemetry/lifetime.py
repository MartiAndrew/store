import logging

from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aio_pika import AioPikaInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import (
    CONTAINER_NAME,
    DEPLOYMENT_ENVIRONMENT,
    KUBERNETES_NAMESPACE_NAME,
    SERVICE_NAME,
    SERVICE_VERSION,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from opentelemetry.trace import set_tracer_provider

from common.opentelemetry.patch_aio_pika import patch_spanbuilder_set_channel

from configuration import constants
from configuration.settings import settings


def setup_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Включить opentelemetry.

    :param app: current application.
    """
    if not settings.telemetry.enable or not settings.telemetry.endpoint:
        return

    sampler = ParentBasedTraceIdRatio(settings.telemetry.trace_rate)

    tracer_provider = TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: constants.SERVICE_NAME_LOWER,
                TELEMETRY_SDK_LANGUAGE: "python",
                DEPLOYMENT_ENVIRONMENT: settings.environment,
                KUBERNETES_NAMESPACE_NAME: settings.namespace,
                SERVICE_VERSION: settings.version,
                CONTAINER_NAME: settings.hostname,
            },
        ),
        sampler=sampler,
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.telemetry.endpoint,
                insecure=True,
            ),
        ),
    )

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
        "/metrics",
    ]

    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls=",".join(excluded_endpoints),
    )
    RedisInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    AioPikaInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    patch_spanbuilder_set_channel()
    LoggingInstrumentor().instrument(
        tracer_provider=tracer_provider,
        set_logging_format=True,
        log_level=logging.getLevelName(settings.logging.log_level.value),
    )

    set_tracer_provider(tracer_provider=tracer_provider)


def stop_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Отключить opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.telemetry.enable or not settings.telemetry.endpoint:
        return

    FastAPIInstrumentor().uninstrument_app(app)
    RedisInstrumentor().uninstrument()
    AioPikaInstrumentor().uninstrument()
    LoggingInstrumentor().uninstrument()
