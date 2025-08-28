from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class ServiceRedisSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}SERVICE_REDIS_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Variables for Redis
    host: str = "localhost"
    port: int = 6379
    user: str = ""
    password: str = ""
    base: int = 0
    retry_on_error_backoff: int = 1
    number_retries_on_error: int = 60
    default_ttl: int = 86400
    redis_scan_count: int = 100

    @property
    def url(self) -> URL:
        """
        Собрать REDIS URL из настроек.

        :return: redis URL.
        """
        path = ""
        if self.base is not None:
            path = f"/{self.base}"
        return URL.build(
            scheme="redis",
            host=self.host,
            port=self.port,
            user=self.user or None,
            password=self.password or None,
            path=path,
        )
