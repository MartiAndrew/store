from typing import Union

import aio_pika
import aiormq
from loguru import logger
from yarl import URL


async def init_queue(  # noqa: WPS211
    queue_name: str,
    routing_key: str,
    exchange_name: str,
    broker_url: Union[str, URL],
    is_queue_durable: bool,
    is_exchange_durable: bool,
) -> None:
    """
    Инициализация эксченджей и очередей и их бинд.

    :param queue_name: queues name.
    :param routing_key: rounting key.
    :param exchange_name: exchange name.
    :param broker_url: broker url.
    :param is_queue_durable: should the queues be declared as durable.
    :param is_exchange_durable: should the exchange be declared as durable.
    """
    connection = await aio_pika.connect_robust(broker_url, timeout=1)
    async with connection:
        channel = await connection.channel()
        try:
            await channel.get_exchange(exchange_name, ensure=True)
        except aiormq.exceptions.ChannelClosed:
            logger.info(
                "Отсутствует exchange {0}. Декларируем новый exchange",
                exchange_name,
            )
            channel = await connection.channel()
            await channel.declare_exchange(
                exchange_name,
                type=aio_pika.ExchangeType.TOPIC,
                durable=is_exchange_durable,
            )
        logger.info(
            "Задекларирован exchange {0}, durable={1}",
            exchange_name,
            is_exchange_durable,
        )
        queue = await channel.declare_queue(
            queue_name,
            auto_delete=False,
            durable=is_queue_durable,
        )
        logger.info(
            "Задекларирована очередь {0}, durable={1}",
            queue_name,
            is_queue_durable,
        )

        await queue.bind(exchange_name, routing_key=routing_key)
        logger.info("Осуществлен bind очереди к exchange по ключу {0}", routing_key)


async def init_queue_with_dead_letter(  # noqa: WPS211, WPS213
    queue_name: str,
    routing_key: str,
    delay_letter_queue_name: str,
    delay_letter_routing_key: str,
    delay_letter_ttl: int,
    dead_message_queue_name: str,
    dead_message_routing_key: str,
    exchange_name: str,
    broker_url: Union[str, URL],
    is_queue_durable: bool,
    is_exchange_durable: bool,
) -> None:
    """
    Инициализация эксченджей и очередей с dead_letter и их бинд.

    :param queue_name: queue name.
    :param routing_key: routing key.
    :param delay_letter_queue_name: delay letter queue name.
    :param delay_letter_routing_key: delay letter routing key.
    :param delay_letter_ttl: delay letter queue ttl in seconds.
    :param dead_message_queue_name: dead message queue name.
    :param dead_message_routing_key: dead message routing key.
    :param exchange_name: exchange name.
    :param broker_url: broker url.
    :param is_queue_durable: should the queues be declared as durable.
    :param is_exchange_durable: should the exchange be declared as durable.
    """
    connection = await aio_pika.connect_robust(broker_url, timeout=1)
    async with connection:
        channel = await connection.channel()

        await channel.declare_exchange(
            exchange_name,
            type=aio_pika.ExchangeType.TOPIC,
            durable=is_exchange_durable,
            passive=True,
        )
        logger.info(
            "Задекларирован exchange {0}, durable={1}",
            exchange_name,
            is_exchange_durable,
        )

        queue = await channel.declare_queue(
            queue_name,
            auto_delete=False,
            durable=is_queue_durable,
        )
        logger.info(
            f"Задекларирована очередь {queue_name}, durable={is_queue_durable}",
        )

        delay_letter_queue = await channel.declare_queue(
            delay_letter_queue_name,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": queue_name,
                "x-message-ttl": delay_letter_ttl * 1000,  # TTL in milliseconds
            },
        )
        logger.info(f"Задекларирована очередь {delay_letter_queue_name}")

        dead_message_queue = await channel.declare_queue(
            dead_message_queue_name,
            auto_delete=False,
            durable=True,
        )
        logger.info(f"Задекларирована очередь {dead_message_queue_name}")

        await queue.bind(exchange_name, routing_key=routing_key)
        logger.info(
            f"Осуществлен bind очереди {queue_name} к exchange "
            f"по ключу {routing_key}",
        )
        await delay_letter_queue.bind(
            exchange_name,
            routing_key=delay_letter_routing_key,
        )
        logger.info(
            f"Осуществлен bind очереди {delay_letter_queue_name} к exchange "
            f"по ключу {delay_letter_routing_key}",
        )
        await dead_message_queue.bind(
            exchange_name,
            routing_key=dead_message_routing_key,
        )
        logger.info(
            f"Осуществлен bind очереди {dead_message_queue_name} к exchange "
            f"по ключу {dead_message_routing_key}",
        )
