import uuid
from typing import AsyncGenerator, Optional

import aio_pika
import pytest
from aio_pika.abc import AbstractExchange, AbstractIncomingMessage, AbstractQueue
from yarl import URL

from common.rabbitmq.connection import RabbitConnection

from configuration.settings import settings


@pytest.fixture(scope="session")
def rabbit_url() -> URL:
    """
    Фикстура для получения URL брокера.

    :return: урл брокера.
    """
    return settings.rabbit.url


@pytest.fixture(scope="module")
def queue_name() -> str:
    """
    Фикстура для получения названия очереди.

    :return: название очереди.
    """
    return uuid.uuid4().hex


@pytest.fixture(scope="module")
def exchange_name() -> str:
    """
    Фикстура для получения названия exchange.

    :return: название exchange.
    """
    return uuid.uuid4().hex


@pytest.fixture(scope="module")
def routing_key() -> str:
    """
    Фикстура для получения routing key.

    :return: routing key.
    """
    return uuid.uuid4().hex


class QueueInterface:
    """Специальный класс для взаимодействия с тестовой очередью."""

    def __init__(
        self,
        queue: AbstractQueue,
        exchange: AbstractExchange,
        routing_key: str,
    ):
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key

    async def get_message(self) -> Optional[AbstractIncomingMessage]:
        """
        Метод получения сообщения из очереди, если оно есть.

        :return: сообщение из очереди
        """
        return await self.queue.get(fail=False)

    async def is_empty(self) -> bool:
        """
        Метод проверки наличия сообщений в очереди.

        :return: bool есть ли сообщение в очереди
        """
        return await self.queue.get(fail=False, no_ack=True) is None

    async def publish_message(
        self,
        message: str,
    ) -> None:
        """
        Метод добавления сообщения в очередь.

        :param message: сообщение, которое нужно добавить.
        """
        await self.exchange.publish(
            aio_pika.Message(
                bytes(message, "utf-8"),
            ),
            self.routing_key,
        )

    @property
    def name(self) -> str:
        """
        Получить название очереди.

        :return: название очереди.
        """
        return self.queue.name


@pytest.fixture
async def queue(
    rabbit_url: str,
    queue_name: str,
    exchange_name: str,
    routing_key: str,
) -> AsyncGenerator[QueueInterface, None]:
    """
    Создание очереди для тестов.

    :yields: QueueInterface для взаимодействия с очередью.
    """
    connection = await aio_pika.connect_robust(
        rabbit_url,
    )
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(exchange_name)
        queue = await channel.declare_queue(queue_name)
        await queue.bind(exchange, routing_key)

        yield QueueInterface(queue, exchange, routing_key)

        await queue.unbind(exchange, routing_key)
        await queue.delete()
        await exchange.delete()
        await channel.close()


async def rabbitmq_connection_init(rabbit_url: str):
    """
    Создать пул коннектов к RMQ сервиса.

    :return: Пул коннектов к RMQ проекта.
    """
    return RabbitConnection(
        url=settings.rabbit.url,
        exchange=uuid.uuid4().hex,
    )


async def rabbitmq_connection_close(rabbitmq_connection: RabbitConnection):
    """
    Закрыть пул коннектов к БД сервиса.

    :param rabbitmq_connection: Пул коннектов к RMQ проекта.
    """
    await rabbitmq_connection.close_pool()
