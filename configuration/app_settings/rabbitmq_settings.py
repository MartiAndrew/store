from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import ENV_PREFIX


class RabbitSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}RABBITMQ_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: types.VaultRabbitStr = types.VaultRabbitStr("localhost")
    port: types.VaultRabbitInt = types.VaultRabbitInt(5672)  # noqa: WPS432
    user: types.VaultRabbitStr = types.VaultRabbitStr("guest")
    password: types.VaultRabbitStr = types.VaultRabbitStr("guest")
    prefetch_count: types.VaultRabbitInt = types.VaultRabbitInt(100)
    store_exchange: types.VaultRabbitStr = types.VaultRabbitStr("template")
    max_channels_size: types.VaultRabbitInt = types.VaultRabbitInt(100)
    max_connections_size: types.VaultRabbitInt = types.VaultRabbitInt(10)

    @property
    def url(self) -> URL:
        """
        Собрать RabbitMQ URL из настроек.

        :return: RabbitMQ URL.
        """
        return URL.build(
            scheme="ampq",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            path="/",
        )
