from aio_pika.abc import AbstractChannel
from opentelemetry.semconv.trace import SpanAttributes


def patch_spanbuilder_set_channel() -> None:
    """
    Патч aio_pika telemetry.

    https://github.com/open-telemetry/opentelemetry-python-contrib/issues/1835
    """
    import opentelemetry.instrumentation.aio_pika.span_builder  # noqa: WPS433, WPS301
    from opentelemetry.instrumentation.aio_pika.span_builder import (  # noqa: WPS433, WPS301, E501, WPS458
        SpanBuilder,
    )

    def set_channel(  # noqa: WPS430
        self: SpanBuilder,
        channel: AbstractChannel,
    ) -> None:
        if getattr(channel, "_connection", None):
            url = channel._connection.url  # type: ignore # noqa: WPS437
            self._attributes.update(
                {
                    SpanAttributes.NET_PEER_NAME: url.host,
                    SpanAttributes.NET_PEER_PORT: url.port,
                },
            )
        else:
            self._attributes.update(
                {
                    SpanAttributes.NET_PEER_NAME: "",
                    SpanAttributes.NET_PEER_PORT: 5672,  # type: ignore
                },
            )

    opentelemetry.instrumentation.aio_pika.span_builder.SpanBuilder.set_channel = (  # type: ignore # noqa: WPS219, E501
        set_channel  # type: ignore[misc]
    )
