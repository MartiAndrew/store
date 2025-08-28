from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class WebSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}WEB_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
    )

    host: str = "127.0.0.1"
    port: int = 8000
    # количество веб-воркеров
    workers_count: int = 1
    # Live-reload uvicorn
    reload: bool = False
    # При превышении лимита попыток получить коннект убивать процесс
    kill_pod_by_db_pool_timeout: bool = False
    # Макс кол-во попыток получить коннект
    pool_timeout_errors_limit: int = 3
