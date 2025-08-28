from taskiq import InMemoryBroker, PrometheusMiddleware, TaskiqEvents, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker

from common.logging.logging import init_logger
from common.sentry.sentry import init_sentry

from configuration.clients import TaskiqClientsState
from configuration.settings import settings


def get_rabbit_broker() -> AioPikaBroker:
    """
    Возвращает брокера для taskiq.

    :return: AioPikaBroker
    """
    return AioPikaBroker(
        url=settings.taskiq.rabbit_dsn,
        exchange_name=settings.taskiq.exchange_name,
        delay_queue_name=settings.taskiq.delay_queue_name,
        queue_name=settings.taskiq.queue_name,
        dead_letter_queue_name=settings.taskiq.dead_letter_queue_name,
    ).with_middlewares(
        PrometheusMiddleware(
            server_addr=settings.taskiq.prometheus_host,
            server_port=settings.taskiq.prometheus_port,
        ),
    )


if settings.environment == "pytest" or not getattr(settings, "taskiq", None):
    rabbit_broker = InMemoryBroker()
else:
    rabbit_broker = get_rabbit_broker()
scheduler = TaskiqScheduler(
    broker=rabbit_broker,
    sources=[LabelScheduleSource(rabbit_broker)],
)


@rabbit_broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    """
    Хук при старте воркера.

    :param state: состояние воркера.
    """
    init_logger()
    init_sentry()
    taskiq_clients: TaskiqClientsState = await TaskiqClientsState.clients_startup()
    state.clients = taskiq_clients


@rabbit_broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    """
    Хук при стопе воркера.

    :param state: состояние воркера.
    """
    await state.clients.clients_shutdown()
