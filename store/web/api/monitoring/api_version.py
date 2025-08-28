from pydantic import BaseModel
from starlette import status

from configuration.settings import settings
from store.web.api.monitoring.router import monitoring_router


class VersionResponse(BaseModel):
    """Ответ на запрос версии проекта."""

    version: str
    commit_hash: str


@monitoring_router.get(
    "/version",
    responses={status.HTTP_200_OK: {"model": VersionResponse}},
)
def version() -> VersionResponse:
    """
    Информация по версии приложения.

    :returns: текущую версию приложения и номер коммита.
    """
    return VersionResponse(
        version=settings.version,
        commit_hash=settings.commit_hash,
    )
