import asyncio
import json
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Coroutine, Dict, Type, TypeVar

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from loguru import logger
from pydantic import TypeAdapter, ValidationError
from yarl import URL

from common.base_workers import metrics, workers_health
from common.base_workers.decorators import message_logging
from common.base_workers.types import SupportsWorkerClientState
from common.logging.logging import init_logger
from common.rabbitmq.queues import init_queue, init_queue_with_dead_letter
from common.rabbitmq.vector_producer import VectorProducer
from common.sentry.sentry import init_sentry

MessageData = TypeVar("MessageData")


class NeedDelayedRetryException(Exception):  # noqa: N818
    """Сообщение необходимо перезапустить через время."""


class NeedSendDeadMessageException(Exception):  # noqa: N818
    """Сообщение необходимо отправить в мёртвую очередь."""


class BaseWorker(ABC):
    """Базовый интерфейс воркера."""

    @abstractmethod
    async def run(self) -> None:
        """Запустить воркер."""


class BaseRabbitWorker(BaseWorker, ABC):  # noqa: WPS230
    """Базовый воркер для обработки событий из кролика."""

    def __init__(  # noqa: WPS211
        self,
        message_class: Type[MessageData],
        callback: Callable[[MessageData, Any], Coroutine[Any, Any, Any]],
        queue_name: str,
        routing_key: str,
        exchange_name: str,
        broker_url: str | URL,
        prefetch_count: int,
        metrics_host: str,
        metrics_port: int,
        health_host: str,
        health_port: int,
        enable_health_check: bool,
        clients_state_class: Type[SupportsWorkerClientState] | None,
        is_queue_durable: bool = False,
        is_vector: bool = False,
        is_exchange_durable: bool = False,
    ):
        self.message_class = message_class
        self.callback = callback
        self.queue_name = queue_name
        self.broker_url = broker_url
        self.metrics_host = metrics_host
        self.metrics_port = metrics_port
        self.health_host = health_host
        self.health_port = health_port
        self.enable_health_check = enable_health_check
        self.is_queue_durable = is_queue_durable
        self.is_vector = is_vector
        self._prefetch_count = prefetch_count
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.is_exchange_durable = is_exchange_durable
        self.clients: SupportsWorkerClientState | None = None
        self._consumer_tag: str = ""
        self.clients_state_class = clients_state_class
        self._type_adapter = TypeAdapter(self.message_class)
        celery_type = tuple[
            list[Any],
            dict[str, Any],
            dict[Any, Any],
        ]
        self._celery_type_adapter = TypeAdapter(celery_type)

    async def startup(self):
        """Функция для запуска настроек и коннектов перед стартом."""
        init_logger()
        init_sentry()
        if self.metrics_host:
            metrics.run_metrics_server(self.metrics_host, self.metrics_port)
        if self.clients_state_class:
            clients = await self.clients_state_class.clients_startup()
            self.clients = clients
            if self.enable_health_check:
                workers_health.start_wsgi_server(
                    self.clients,
                    self.health_port,
                    self.health_host,
                )
        await init_queue(
            self.queue_name,
            self.routing_key,
            self.exchange_name,
            self.broker_url,
            self.is_queue_durable,
            self.is_exchange_durable,
        )
        logger.info("Воркер запущен")

    async def shutdown(self):
        """Функция для остановки коннектов перед стартом."""
        if self.clients:
            await self.clients.clients_shutdown()
        logger.info("Воркер остановлен")

    @asynccontextmanager
    async def _queue(self) -> AsyncGenerator[AbstractQueue, None]:
        """
        Получить объект очереди.

        :yield: очередь.
        """
        connection = await aio_pika.connect_robust(self.broker_url, timeout=1)
        async with connection, connection.channel() as channel:  # noqa: WPS316
            await channel.set_qos(prefetch_count=self._prefetch_count)
            logger.info(
                "Декларируем очередь {0}, durable={1}, prefetch_count={2}",
                self.queue_name,
                self.is_queue_durable,
                self._prefetch_count,
            )
            queue = await channel.declare_queue(
                self.queue_name,
                auto_delete=False,
                durable=self.is_queue_durable,
            )
            yield queue

    @message_logging
    async def _process_message(  # noqa: WPS213
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        """
        Обработка сообщения из кролика.

        :param message: message from the queues.
        """
        start_time = time.monotonic()
        try:
            async with message.process(requeue=True, ignore_processed=True):
                logger.debug("Получили сообщение из очереди.")
                metrics.incoming_messages_count.labels(self.queue_name).inc(1)

                parsed_message = self._parse_message(message)
                if not parsed_message:
                    metrics.wrong_formatted_messages_count.labels(
                        self.queue_name,
                    ).inc(1)
                    return

                logger.debug("Начинаем обрабатывать сообщение.")  # type: ignore
                await self.callback(parsed_message, self.clients)
        except Exception as exc:
            logger.exception("Unknown error {0}", exc)
            metrics.processing_errors_count.labels(self.queue_name).inc(1)
        else:
            logger.debug("Обработали сообщение из очереди.")  # type: ignore
            metrics.successful_messages_count.labels(self.queue_name).inc(1)
        finally:
            metrics.execution_message_time.labels(
                self.queue_name,
            ).observe(
                time.monotonic() - start_time,
            )

    def _parse_message(self, message: AbstractIncomingMessage) -> MessageData | None:
        """
        Парсинг и декодинг сообщения из кролика.

        :param message: message from the queues.
        :return: parsed message on success else None.
        """
        message_body = None
        try:
            message_text = message.body.decode("utf-8")
            logger.debug("Входящее сообщение: {0}", message_text)
            if self.is_vector:
                return self._parse_celery(message_text)
            return self._parse_json(message_text)
        except (
            json.decoder.JSONDecodeError,
            ValidationError,
            TypeError,
            ValueError,
        ) as exc:
            logger.error(
                "Неверный формат сообщения {0}, подробнее: {1}",
                message_body,
                exc,
            )
            return None

    def _parse_json(self, message_text: str) -> MessageData:  # type: ignore
        """
        Парсинг json сообщения.

        :param message_text: string to parse.
        :return: parsed message.
        """
        return self._type_adapter.validate_json(message_text)

    def _parse_celery(self, message_text: str) -> MessageData:  # type: ignore
        """
        Парсинг celery сообщения.

        :param message_text: string to parse.
        :return: parsed message.
        """
        message = self._celery_type_adapter.validate_json(message_text)
        return self.message_class(*message[0], **message[1])


class Worker(BaseRabbitWorker):
    """
    Воркер для обработки одиночных сообщений из очереди.

    Для каждого сообщения происходит валидация и вызов колбэка.
    """

    async def run(self):
        """Старт воркера."""
        await self.startup()
        try:
            async with self._queue() as queue:
                self._consumer_tag = await queue.consume(self._process_message)
                await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("Воркер прерван")
        finally:
            await self.shutdown()


class WorkerWithDeadMessage(Worker):  # noqa: WPS230
    """
    Воркер для обработки одиночных сообщений из очереди с использованием dead_messages.

    Для каждого сообщения происходит валидация и вызов колбэка.
    """

    def __init__(  # noqa: WPS211
        self,
        *args: Any,
        delay_letter_queue_name: str,
        delay_letter_routing_key: str,
        delay_letter_ttl: int,
        dead_message_queue_name: str,
        dead_message_routing_key: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.delay_letter_queue_name = delay_letter_queue_name
        self.delay_letter_routing_key = delay_letter_routing_key
        self.delay_letter_ttl = delay_letter_ttl
        self.dead_message_queue_name = dead_message_queue_name
        self.dead_message_routing_key = dead_message_routing_key

    async def publish_message(
        self,
        routing_key: str,
        parsed_message: MessageData | None,
        message_headers: Dict | None = None,
    ) -> None:
        """
        Отправить сообщение в очередь.

        :param routing_key: Ключ маршрутизации.
        :param parsed_message: Объект сообщения.
        :param message_headers: Заголовки сообщения.
        """
        logger.info(f"Отправляем сообщение по ключу {routing_key}")
        vector_producer = VectorProducer(self.broker_url)
        vector_producer.publisher._exchange_declared = True  # noqa: WPS437
        try:
            await vector_producer.publish_to_exchange(
                routing_key,
                parsed_message,  # type: ignore
                message_headers,
            )
        except Exception as exc:
            logger.exception(exc)
            await vector_producer.publisher.close_pool()
        else:
            await vector_producer.publisher.close_pool()

    async def startup(self):
        """Функция для запуска настроек и коннектов перед стартом."""
        init_logger()
        init_sentry()
        if self.metrics_host:
            metrics.run_metrics_server(self.metrics_host, self.metrics_port)
        if self.clients_state_class:
            clients = await self.clients_state_class.clients_startup()
            self.clients = clients
            if self.enable_health_check:
                workers_health.start_wsgi_server(
                    self.clients,
                    self.health_port,
                    self.health_host,
                )
        await init_queue_with_dead_letter(
            self.queue_name,
            self.routing_key,
            self.delay_letter_queue_name,
            self.delay_letter_routing_key,
            self.delay_letter_ttl,
            self.dead_message_queue_name,
            self.dead_message_routing_key,
            self.exchange_name,
            self.broker_url,
            self.is_queue_durable,
            self.is_exchange_durable,
        )
        logger.info("Воркер запущен")

    @asynccontextmanager
    async def _queue(self) -> AsyncGenerator[AbstractQueue, None]:
        """
        Получить объект очереди.

        :yield: очередь.
        """
        connection = await aio_pika.connect_robust(self.broker_url, timeout=1)
        async with connection, connection.channel() as channel:  # noqa: WPS316
            await channel.set_qos(prefetch_count=self._prefetch_count)
            logger.info(
                "Декларируем очередь {0}, durable={1}, prefetch_count={2}",
                self.queue_name,
                self.is_queue_durable,
                self._prefetch_count,
            )
            queue = await channel.declare_queue(
                self.queue_name,
                auto_delete=False,
                durable=self.is_queue_durable,
            )
            yield queue

    @message_logging
    async def _process_message(  # noqa: WPS213
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        """
        Обработка сообщения из кролика.

        :param message: message from the queues.
        """
        start_time = time.monotonic()

        async with message.process(ignore_processed=True):
            logger.debug("Получили сообщение из очереди.")

            metrics.incoming_messages_count.labels(self.queue_name).inc(1)

            parsed_message = self._parse_message(message)
            if not parsed_message:
                metrics.wrong_formatted_messages_count.labels(
                    self.queue_name,
                ).inc(1)
                return

            message_headers = message.headers  # type: ignore
            logger.info(f"Message headers: {message.info()}")

            try:
                logger.debug("Начинаем обрабатывать сообщение.")
                await self.callback(
                    parsed_message,
                    self.clients,
                    message_headers,  # type: ignore
                )
            except NeedDelayedRetryException:
                logger.warning("Отложенный перезапуск сообщения")
                metrics.delayed_message_count.labels(self.queue_name).inc(1)
                await message.nack(requeue=False)
                retry_count = message_headers.get("retry_count", 0)
                await self.publish_message(
                    self.delay_letter_routing_key,
                    parsed_message,
                    {"retry_count": retry_count + 1},
                )
            except NeedSendDeadMessageException:
                logger.warning("Отправка сообщения в dead-message очередь")
                metrics.dead_message_count.labels(self.queue_name).inc(1)
                await message.nack(requeue=False)
                await self.publish_message(
                    self.dead_message_routing_key,
                    parsed_message,
                )
            except Exception as exc:
                logger.exception("Unknown error {0}", exc)
                metrics.processing_errors_count.labels(self.queue_name).inc(1)
            else:
                logger.debug("Обработали сообщение из очереди.")  # type: ignore
                metrics.successful_messages_count.labels(self.queue_name).inc(1)
                await message.ack()
            finally:
                metrics.execution_message_time.labels(
                    self.queue_name,
                ).observe(
                    time.monotonic() - start_time,
                )


class BatchWorker(BaseRabbitWorker):
    """
    Воркер для единовременной обработки нескольких сообщений из очереди.

    Воркер вычитывет несколько сообщений, валидирует их, формирует единую пачку
    и вызывает колбэка с этой пачкой.
    """

    def __init__(  # noqa: WPS211
        self,
        *args: Any,
        batch_size: int,
        batch_timeout: float,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._pending_messages: asyncio.Queue[AbstractIncomingMessage] = asyncio.Queue(
            maxsize=batch_size,
        )
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout

    async def run(self) -> None:  # noqa: D102
        await self.startup()

        try:  # noqa: WPS501
            async with self._queue() as queue:
                consumer_tag = await queue.consume(self._on_message)
                try:  # noqa: WPS505
                    await self._run_main_loop()
                except asyncio.CancelledError:
                    logger.info("Завершение работы воркера...")
                finally:
                    await queue.cancel(consumer_tag)
                    message = None
                    while not self._pending_messages.empty():
                        message = self._pending_messages.get_nowait()
                    if message:
                        await message.nack(multiple=True)
        finally:
            await self.shutdown()

    async def _on_message(self, message: AbstractIncomingMessage) -> None:
        """
        Метод, который выполняется при каждом новом сообщении из кролика.

        Складывает сообщения во внутреннюю очередь,
        из которой набирается пачка.
        :param message: входящее сообщение.
        """
        await self._pending_messages.put(message)

    async def _get_messages(self) -> list[AbstractIncomingMessage]:
        """
        Получить пачку сообщений.

        Блокирует выполнение до получения первого сообщения, далее в течение заданного
        времени пытается донабрать сообщения.
        :return: пачка с сообщениями.
        """
        logger.debug("Ожидаем первое сообщение в пачке...")
        messages = [await self._pending_messages.get()]
        logger.debug("Получено первое сообщение из очереди.")

        current_timeout = self._batch_timeout
        for _ in range(1, self._batch_size):
            start_time = time.monotonic()
            try:
                logger.debug(
                    "Ожидаем сообщение в течение {current_timeout} секунд...",
                    current_timeout=current_timeout,
                )
                message = await asyncio.wait_for(
                    self._pending_messages.get(),
                    current_timeout,
                )
            except asyncio.TimeoutError:
                logger.debug("Время ожидания вышло.")
                break

            end_time = time.monotonic()
            logger.debug("Получено сообщение из очереди.")
            messages.append(message)

            current_timeout = current_timeout - (end_time - start_time)

        logger.debug(
            "Сформирована пачка сообщений длиной {messages_len}",
            messages_len=len(messages),
        )
        return messages

    async def _run_main_loop(self) -> None:  # noqa: WPS213
        """
        Основной цикл работы воркера.

        :raises asyncio.CancelledError: в случае перехвата данного исключения.
        """
        while True:
            start_time = time.monotonic()
            messages = await self._get_messages()
            metrics.incoming_messages_count.labels(self.queue_name).inc(len(messages))

            logger.debug("Валидация сообщений из пачки.")
            parsed_messages = [self._parse_message(message) for message in messages]
            parsed_messages = [message for message in parsed_messages if message]

            logger.debug("Начинаем обрабатывать пачку сообщений...")
            logger.debug(parsed_messages)
            try:
                if parsed_messages:
                    await message_logging(self.callback)(
                        parsed_messages,
                        self.clients,
                    )
            except asyncio.CancelledError:
                await messages[-1].nack(multiple=True)
                metrics.processing_errors_count.labels(self.queue_name).inc(
                    len(parsed_messages),
                )
                raise
            except Exception as exc:
                logger.exception(exc)
                await messages[-1].nack(multiple=True)
                metrics.processing_errors_count.labels(self.queue_name).inc(
                    len(parsed_messages),
                )
                continue

            logger.debug("Обработали пачку сообщений.")
            await messages[-1].ack(multiple=True)
            metrics.successful_messages_count.labels(self.queue_name).inc(
                len(parsed_messages),
            )
            metrics.wrong_formatted_messages_count.labels(self.queue_name).inc(
                len(messages) - len(parsed_messages),
            )
            metrics.execution_message_time.labels(
                self.queue_name,
            ).observe(
                time.monotonic() - start_time,
            )
