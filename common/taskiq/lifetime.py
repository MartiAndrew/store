from common.taskiq.broker import rabbit_broker

from configuration.settings import settings


async def setup_taskiq() -> None:
    """Запустить брокера для taskiq."""
    if getattr(settings, "taskiq", None) and settings.taskiq.enable:
        await rabbit_broker.startup()


async def stop_taskiq() -> None:
    """Остановить брокера для taskiq."""
    if getattr(settings, "taskiq", None) and settings.taskiq.enable:
        await rabbit_broker.shutdown()
