import logging

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import (
    BreadcrumbHandler,
    EventHandler,
    LoggingIntegration,
)
from sentry_sdk.integrations.starlette import StarletteIntegration

from configuration import constants
from configuration.settings import settings


def init_sentry():
    """Инициализация sentry."""
    if not settings.sentry.enable or not settings.sentry.dsn:
        logger.debug(
            "Sentry не настроен. "
            "Убедитесь, что `SENTRY_ENABLE` и `SENTRY_DSN` установлены правильно.",
        )
    else:
        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            environment=settings.environment,
            integrations=[
                LoggingIntegration(),
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
            release=f"{constants.SERVICE_NAME_LOWER}@{settings.version}",
            send_default_pii=True,
            traces_sample_rate=settings.sentry.traces_sample_rate,
        )

        logger.add(
            BreadcrumbHandler(level=logging.DEBUG),
            diagnose=False,
            level=logging.DEBUG,
        )

        logger.add(
            EventHandler(level=logging.ERROR),
            diagnose=False,
            level=logging.ERROR,
        )

        logger.debug(f"Sentry включён {settings.sentry.dsn}")
