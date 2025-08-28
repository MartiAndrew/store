# flake8: noqa
from pydantic import BaseModel

from common.rabbitmq.producer import BaseProducer, RabbitPublisher


class VectorProducer(BaseProducer):
    """Класс для сообщений посылаемых в вектор."""

    def __init__(self, url):
        self.publisher = RabbitPublisher(url=url, exchange="vector")

    @staticmethod
    def get_message(msg: BaseModel) -> bytes:
        """
        Сериализация сообщения для кролика.

        :param msg: Pydantic объект сообщения.
        :return: сериализованное сообщение в виде bytes.
        """
        msg_json = msg.json()
        return f"[[],{msg_json},{{}}]".encode()  # noqa: P103

    async def comment_created_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.created",
            message,
        )

    async def comment_blocked_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.blocked",
            message,
        )

    async def comment_unblocked_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.unblocked",
            message,
        )

    async def comment_updated_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.updated",
            message,
        )

    async def comment_delete_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.deleted",
            message,
        )

    async def comment_deleted_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.deleted",
            message,
        )

    async def comment_report_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.reported",
            message,
        )

    async def comment_report_unregistered_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.comment.reported_unregistered",
            message,
        )

    async def room_comment_created_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.room_comment.created",
            message,
        )

    async def room_comment_deleted_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.room_comment.deleted",
            message,
        )

    async def room_blocked_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.room_comment.blocked",
            message,
        )

    async def room_unblocked_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.room_comment.unblocked",
            message,
        )

    async def open_room_video_comment_deleted_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_video_comment.deleted",
            message,
        )

    async def open_room_comment_deleted_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.deleted",
            message,
        )

    async def open_room_comment_created_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.created",
            message,
        )

    async def open_room_comment_edited_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.edited",
            message,
        )

    async def open_room_comment_reported_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.reported",
            message,
        )

    async def open_room_text_comment_replied(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room.text_comment.replied",
            message,
        )

    async def open_room_video_comment_replied(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room.video_comment.replied",
            message,
        )

    async def open_room_comment_reacted(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.reacted",
            message,
        )

    async def open_room_comment_blocked(self, message: BaseModel):
        await self.publish_to_exchange(
            "acrab.open_room_comment.blocked",
            message,
        )

    async def view_started_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "atik.view_started",
            message,
        )

    async def view_started_rutube_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "rutik.view_started_rutube",
            message,
        )

    async def anonymous_view_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "atik.anonymous_view",
            message,
        )

    async def sorm_video_viewed_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "atik.sorm_video.viewed",
            message,
        )

    async def view_ended_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "atik.view_ended",
            message,
        )

    async def view_ended_rutube_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "rutik.view_ended_rutube",
            message,
        )

    async def audio_viewed_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "atik.audio_viewed",
            message,
        )

    async def audio_viewed_rutube_message(self, message: BaseModel):
        await self.publish_to_exchange(
            "rutik.audio_viewed",
            message,
        )
