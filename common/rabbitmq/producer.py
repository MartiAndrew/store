from typing import Dict

import aio_pika
from loguru import logger
from pydantic import BaseModel

from common.rabbitmq.connection import RabbitConnection


class RabbitPublisher(RabbitConnection):
    """Писатель сообщений в кролик."""

    async def publish_to_exchange(
        self,
        routing_key,
        message: aio_pika.Message,
    ) -> bool:
        """
        Опубликовать сообщение в exchange с указанным ключом роутинга.

        :param message: сообщение для кролика.
        :param routing_key: ключ сообщения.
        :return: было ли сообщение опубликовано.
        """
        try:
            async with self._channel_pool.acquire() as channel:  # type: ignore
                if channel.is_closed:
                    await channel.reopen()
                exchange = await self.get_exchange()
                await exchange.publish(
                    message=message,
                    routing_key=routing_key,
                )
        except (
            aio_pika.AMQPException,
            aio_pika.MessageProcessError,
            aio_pika.exceptions.ChannelClosed,
        ) as exc:
            logger.error(f"Произошла ошибка при публикации сообщения: {exc}")
            return False
        return True


class BaseProducer:
    """Базовый класс для сообщений посылаемых в кролик."""

    publisher: RabbitPublisher

    @staticmethod
    def get_message(msg: BaseModel) -> bytes:
        """
        Сериализация сообщения для кролика.

        :param msg: Pydantic объект сообщения.
        :return: сериализованное сообщение в виде bytes.
        """
        return msg.json().encode()

    async def publish_to_exchange(
        self,
        routing_key: str,
        message: BaseModel,
        headers: Dict | None = None,
    ) -> bool:
        """
        Опубликовать сообщение в exchange с указанным ключом роутинга.

        :param message: Pydantic объект сообщения.
        :param routing_key: ключ сообщения.
        :param headers: заголовки сообщения.
        :return: было ли сообщение опубликовано.
        """
        return await self.publisher.publish_to_exchange(
            routing_key,
            aio_pika.Message(
                body=self.get_message(message),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers=headers or {},
            ),
        )
