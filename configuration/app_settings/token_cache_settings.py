from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class TokenCacheSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}TOKEN_CACHE_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Variables for Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_user: str = ""
    redis_password: str = ""
    redis_base: int = 3
    redis_retry_on_error_backoff: int = 1
    redis_number_retries_on_error: int = 60

    @property
    def redis_url(self) -> URL:
        """
        Собрать REDIS URL из настроек.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user or None,
            password=self.redis_password or None,
            path=path,
        )
