from loguru import logger
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_wsgi_server,
)

from configuration.settings import settings

registry = CollectorRegistry()


incoming_messages_count = Counter(
    "incoming_messages_count",
    "Number of incoming messages",
    ["queue_name"],
    registry=registry,
)

successful_messages_count = Counter(
    "successful_messages_count",
    "Number of successfully processed messages",
    ["queue_name"],
    registry=registry,
)

wrong_formatted_messages_count = Counter(
    "wrong_formatted_messages_count",
    "Number of messages with incorrect format",
    ["queue_name"],
    registry=registry,
)

processing_errors_count = Counter(
    "processing_errors_count",
    "Number of errors during message processing",
    ["queue_name"],
    registry=registry,
)

delayed_message_count = Counter(
    "delayed_message_count",
    "Number of delayed repeated messages",
    ["queue_name"],
    registry=registry,
)
dead_message_count = Counter(
    "dead_message_count",
    "Number of dead messages",
    ["queue_name"],
    registry=registry,
)

execution_message_time = Histogram(
    "execution_message_time",
    "Time of message execution",
    ["queue_name"],
    registry=registry,
)

aggregated_batch_density_uniq_keys = Histogram(
    "aggregated_batch_density_uniq_keys",
    "Density of keys collected in a batch",
    ["worker_name"],
    registry=registry,
)

application_version = Gauge(
    name="application_version",
    documentation="The information of a service version",
    labelnames=["version", "commit_hash"],
)
application_version.labels(settings.version, settings.commit_hash).set(1)


def density_collector(func):  # type:ignore
    """Декоратор для сбора метрик воркеров.

    :param func: callable, функция-агрегатор сообщений
    :returns: callable, декорированная функция
    """

    def wrapper(cls, *args, **kwargs):  # type: ignore
        func_result = func(cls, *args, **kwargs)
        aggregated_batch_density_uniq_keys.labels(
            str(cls.name),
        ).observe(len(func_result))
        return func_result

    return wrapper


def run_metrics_server(host: str, port: int) -> None:
    """
    Запуск сервера отдачи метрик.

    :param host: хост для запуска сервера.
    :param port: порт для запуска сервера.
    """
    logger.info("Запуск сервера для предоставления метрик")
    start_wsgi_server(port, addr=host, registry=registry)
    logger.info(
        "Сервер для предоставления метрик запущен на {host}:{port}",
        host=host,
        port=port,
    )
