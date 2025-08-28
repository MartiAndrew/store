import enum

from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Возможные уровни логирования."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"  # noqa: WPS110
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class LoggingSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}LOGGER_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Вывод лога в одну строку (актуально для трейсов в графане)
    log_in_one_line: bool = True
    # Вывод SQL запросов в логах
    db_echo: bool = False
    # уровень логирования
    log_level: LogLevel = LogLevel.INFO
    # уровень логирования библиотек
    lib_log_level: LogLevel = LogLevel.INFO
    # Если True, то в логе выводится json ответ от ручки.
    echo_response_body: bool = True
