from common.rabbitmq.connection import RabbitConnection

from configuration.settings import settings


async def setup_rabbit() -> RabbitConnection:
    """
    Создать пул коннектов к RMQ сервиса.

    :return: Пул коннектов к RMQ проекта.
    """
    return RabbitConnection(
        url=settings.rabbit.url,
        exchange=settings.rabbit.store_exchange,
    )


async def stop_rabbit(rabbitmq_connection: RabbitConnection) -> None:
    """
    Закрыть пул коннектов к БД сервиса.

    :param rabbitmq_connection: Пул коннектов к RMQ проекта.
    """
    await rabbitmq_connection.close_pool()
