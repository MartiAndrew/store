from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class TelemetrySettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}TELEMETRY_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Grpc endpoint for opentelemetry.
    # E.G. http://localhost:4317
    endpoint: str = ""
    enable: bool = True
    trace_rate: float = 0.05
