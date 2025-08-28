from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import ENV_PREFIX, SERVICE_NAME_LOWER


class TaskiqSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}TASKIQ_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enable: bool = True
    rabbit_dsn: types.VaultRabbitStr = types.VaultRabbitStr(
        "amqp://guest:guest@127.0.0.1/",
    )
    exchange_name: types.VaultRabbitStr = types.VaultRabbitStr(
        f"{SERVICE_NAME_LOWER}-taskiq",
    )
    queue_name: types.VaultRabbitStr = types.VaultRabbitStr(
        f"{SERVICE_NAME_LOWER}-taskiq",
    )
    dead_letter_queue_name: types.VaultRabbitStr = types.VaultRabbitStr(
        f"{SERVICE_NAME_LOWER}-taskiq.dead_letter",
    )
    delay_queue_name: types.VaultRabbitStr = types.VaultRabbitStr(
        f"{SERVICE_NAME_LOWER}-taskiq.delay",
    )

    prometheus_host: str = "127.0.0.1"
    prometheus_port: int = 9000
