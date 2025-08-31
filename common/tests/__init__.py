"""Утилиты для тестирования."""
from common.rabbitmq.tests.conftest import (
    exchange_name,
    queue,
    queue_name,
    rabbit_url,
    routing_key,
)

__all__ = [  # noqa: WPS410
    "rabbit_url",
    "queue_name",
    "exchange_name",
    "routing_key",
    "queue",
]
