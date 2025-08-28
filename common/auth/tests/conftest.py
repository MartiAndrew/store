import uuid

import jwt
from pydantic import BaseModel

from configuration.settings import settings


class AuthUser(BaseModel):
    """Класс для удобного тестирования авторизации."""

    user_id: int = 121
    user_uuid: uuid.UUID = uuid.uuid4()
    nickname: str = "tester"
    avatar: str = ""
    rls: str = ""

    @property
    def auth_token(self) -> str:
        """
        Возвращает JWT токен пользователя.

        :return: JWT токен
        """
        return jwt.encode(
            {
                "user_id": self.user_id,
                "uuid": self.user_uuid.hex,
                "nickname": self.nickname,
                "avatar": self.avatar,
                "rls": self.rls,
            },
            key=settings.auth.jwt_signing_key,
        )

    @property
    def auth_headers(self) -> dict[str, str]:
        """
        Возвращает словарь-хедеры для авторизации.

        :return: Auth header
        """
        return {
            "Authorization": f"Bearer {self.auth_token}",
        }
