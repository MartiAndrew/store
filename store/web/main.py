import os
import shutil

import uvicorn

from configuration.constants import SERVICE_NAME_LOWER
from configuration.settings import settings


def set_multiproc_dir() -> None:
    """
    Sets mutiproc_dir env variable.

    This function cleans up the multiprocess directory
    and recreates it. This actions are required by prometheus-client
    to share metrics between processes.

    After cleanup, it sets two variables.
    Uppercase and lowercase because different
    versions of the prometheus-client library
    depend on different environment variables,
    so I've decided to export all needed variables,
    to avoid undefined behaviour.
    """
    shutil.rmtree(settings.prometheus_dir, ignore_errors=True)
    os.makedirs(settings.prometheus_dir, exist_ok=True)
    os.environ["prometheus_multiproc_dir"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )


def main() -> None:
    """Входная точка старта WEB."""
    set_multiproc_dir()
    uvicorn.run(
        f"{SERVICE_NAME_LOWER}.web.application:get_app",
        workers=settings.web.workers_count,
        host=settings.web.host,
        port=settings.web.port,
        reload=settings.web.reload,
        log_level=settings.logging.log_level.value.lower(),
        factory=True,
        log_config=None,
    )


if __name__ == "__main__":
    main()
