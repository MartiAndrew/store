from typing import AsyncGenerator

from aio_pika.exceptions import QueueEmpty
from pydantic import BaseModel, TypeAdapter

from common.rabbitmq.connection import RabbitConnection


class RabbitListener(RabbitConnection):
    """Слушатель сообщений кролика."""

    async def listen(
        self,
        queue_name: str,
        message_class: BaseModel,
    ) -> AsyncGenerator[BaseModel, None]:
        """
        Listen to queue.

        This function listens to queue, parsed to Pydantic model
        yields every new message.

        :param queue_name: queue name
        :param message_class: Pydantic model to parsed
        :yields: parsed broker message.

        """
        while True:  # noqa: WPS457
            try:
                queue = await self.get_queue(queue_name)
                message = await queue.get()
            except QueueEmpty:
                continue

            try:
                msg_data = TypeAdapter(message_class).validate_json(message.body)
            except Exception:
                await message.reject()
                continue
            await message.ack()
            yield msg_data
