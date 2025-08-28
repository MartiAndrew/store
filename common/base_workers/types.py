from typing import Any, Coroutine, Self

from typing_extensions import Protocol


class SupportsWorkerClientState(Protocol):
    @classmethod
    async def clients_startup(cls) -> Self:
        ...

    async def clients_shutdown(self):
        ...

    def get_funcs_for_health_check(self) -> list[Coroutine[Any, Any, dict[str, str]]]:
        ...

    async def health(self) -> dict[str, str]:
        ...
