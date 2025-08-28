from datetime import datetime, timezone
from typing import Any

from fastapi import Request


class HeadersMiddleware:
    """Миддлваря для исходящих хедеров."""

    async def __call__(self, request: Request, call_next: Any) -> Any:
        """
        Миддлваря. Добавляет хедеры.

        :param request: запрос.
        :param call_next: обработчик запроса.
        :returns: ответ на запрос.
        """
        headers_dict = {
            "Current-Server-Time": datetime.now(timezone.utc).isoformat(),
            "X-Frame-Options": "DENY",
            "Content-Language": "ru-ru",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "same-origin",
        }

        response = await call_next(request)

        for key, header in headers_dict.items():
            if (  # noqa:  WPS337
                key not in response.headers.keys()
                and key.lower() not in response.headers.keys()
            ):
                response.headers[key] = header

        return response
