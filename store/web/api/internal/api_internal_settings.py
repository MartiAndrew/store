from fastapi import HTTPException
from starlette import status

from configuration.settings import Settings, settings
from store.web.api.internal.router import internal_router


@internal_router.get(
    "/settings",
    response_model=Settings,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Доступ запрещен"},
    },
)
async def get_settings() -> Settings:
    """
    Получить текущие значения настройек проекта.

    Внутренняя ручка, используется программистами.

    :raises HTTPException: Доступ запрещен (актуально на проде).
    :return: список настроек
    """
    if settings.namespace.lower() == "prod":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен",
        )
    return settings
