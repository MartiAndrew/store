from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from store.web.api.monitoring.router import monitoring_router


@monitoring_router.get("/health")
async def health_check(
    request: Request,
) -> JSONResponse:
    """
    Ручка health.

    Используется кубером для пробок (liveness, readiness).

    :param request: Данные запроса
    :raises HTTPException: если не удалось подключиться к внешним сервисам
    :raises HTTPException: если не удалось подключиться к внешним сервисам
    :return: в случае отсутствия ошибок - пустой ответ
    """
    errors: dict[str, str] = await request.app.state.clients.health()

    if errors:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed request to service",
        )
    return JSONResponse(content={})
