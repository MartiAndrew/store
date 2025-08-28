from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class SentrySettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}SENTRY_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # DSN sentry
    dsn: str = ""
    # Ограничение на кол-во отправляемых трейсов
    traces_sample_rate: float = 0.05
    # рубильник sentry
    enable: bool = True
