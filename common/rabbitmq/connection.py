from typing import Optional, Union

import aio_pika
from aio_pika.abc import (
    AbstractExchange,
    AbstractQueue,
    AbstractRobustConnection,
    ExchangeType,
)
from aio_pika.pool import Pool
from yarl import URL


class RabbitConnection:
    """Коннект к кролику."""

    def __init__(
        self,
        url,
        exchange,
        max_connections_size=None,
        max_channels_size=None,
    ):
        self._channel_pool: Optional[Pool[aio_pika.Channel]] = None
        self._connection_pool: Optional[Pool[aio_pika.Connection]] = None
        self._declared_queues = set()
        self._exchange_declared = False
        self.exchange = exchange

        if not self._connection_pool:
            self._connection_pool = Pool(
                self.get_connection,
                url,
                max_size=max_connections_size,
            )

        async def get_channel() -> aio_pika.Channel:  # noqa: WPS430
            async with self._connection_pool.acquire() as connection:  # type: ignore
                return await connection.channel()  # type: ignore

        if not self._channel_pool:
            self._channel_pool = Pool(
                get_channel,
                max_size=max_channels_size,
            )

    async def get_exchange(self) -> AbstractExchange:
        """
        Функция создания эксчейнджа.

        :return: AbstractExchange
        """
        async with self._channel_pool.acquire() as channel:  # type: ignore
            if self._exchange_declared:
                return await channel.get_exchange(self.exchange)
            exchange = await channel.declare_exchange(
                self.exchange,
                type=ExchangeType.TOPIC,
            )
            self._exchange_declared = True
            return exchange

    async def get_queue(self, name: str) -> AbstractQueue:
        """
        Функция создания очереди.

        :param name: queue name
        :return: AbstractQueue
        """
        async with self._channel_pool.acquire() as channel:  # type: ignore
            if name in self._declared_queues:
                return await channel.get_queue(name)
            queue = await channel.declare_queue(name)
            await queue.bind(await self.get_exchange())
            self._declared_queues.add(name)
            return queue

    async def queue_bind(self, queue_name: str, routing_key: str) -> None:
        """
        Функция биндинга очереди.

        :param queue_name: queue name
        :param routing_key: routing key
        """
        queue = await self.get_queue(queue_name)
        await queue.bind(await self.get_exchange(), routing_key)

    @staticmethod
    async def get_connection(url: Union[str, URL]) -> AbstractRobustConnection:
        """
        Создать connection к кролику.

        :param url: rabbit url
        :return: AbstractRobustConnection
        """
        return await aio_pika.connect_robust(url)

    async def close_pool(self) -> None:
        """Закрывает пул соединений."""
        if self._channel_pool is not None:
            await self._channel_pool.close()
            self._channel_pool = None
        if self._connection_pool is not None:
            await self._connection_pool.close()
            self._channel_pool = None
