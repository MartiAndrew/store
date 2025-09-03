import json
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT, TEMP_DIR

from configuration.app_settings.auth_settings import AuthSettings
from configuration.app_settings.locale_settings import LocaleSettings
from configuration.app_settings.logging_settings import LoggingSettings
from configuration.app_settings.sentry_settings import SentrySettings
from configuration.app_settings.service_db_settings import ServiceDbSettings
from configuration.app_settings.telemetry_settings import TelemetrySettings
from configuration.app_settings.web_settings import WebSettings
from configuration.constants import ENV_PREFIX


class Settings(BaseSettings):
    """
    Настройки приложения.

    Отдельные сервисы выделены в отдельные классы.
    В секции if TYPE_CHECKING подключены все существующие сервисы из common.
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        json_schema_extra={"examples": [{}]},
    )

    # Хеш коммита (проставляется в докере из гитлаба)
    commit_hash: str = ""
    # Окружение
    environment: str = "dev"
    # флаг дебага
    debug: bool = False
    # Имя хоста (кубер)
    hostname: str = Field(alias="HOSTNAME", default="UNKNOWN")

    # WEB настройки
    web: WebSettings = WebSettings()

    # Sentry
    sentry: SentrySettings = SentrySettings()
    # Logging (зависит от auth)
    logging: LoggingSettings = LoggingSettings()
    # Телеметрия
    telemetry: TelemetrySettings = TelemetrySettings()
    # Prometheus
    prometheus_dir: Path = TEMP_DIR.joinpath("prom")
    # Auth
    auth: AuthSettings = AuthSettings()
    # Localization
    locale: LocaleSettings = LocaleSettings()
    # Не удалять строчку, по ней идет поиск

    service_db: ServiceDbSettings = ServiceDbSettings()

    if TYPE_CHECKING:  # noqa: WPS604
        # TYPE_CHECKING elasticsearch
        from configuration.app_settings.elasticsearch_settings import (
            ElasticsearchSettings,
        )

        elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
        # TYPE_CHECKING sqlalchemy
        from configuration.app_settings.sqlalchemy_db_settings import (
            SQLAlchemyDbSettings,
        )

        sqlalchemy_db: SQLAlchemyDbSettings = SQLAlchemyDbSettings()
        # TYPE_CHECKING rabbitmq
        from configuration.app_settings.rabbitmq_settings import RabbitSettings

        rabbit: RabbitSettings = RabbitSettings()
        # TYPE_CHECKING service_redis
        from configuration.app_settings.service_redis_settings import (
            ServiceRedisSettings,
        )

        service_redis: ServiceRedisSettings = ServiceRedisSettings()
        # TYPE_CHECKING token_cache
        from configuration.app_settings.token_cache_settings import TokenCacheSettings

        token_cache: TokenCacheSettings = TokenCacheSettings()
        # TYPE_CHECKING taskiq
        from configuration.app_settings.taskiq_settings import TaskiqSettings

        taskiq: TaskiqSettings = TaskiqSettings()
        # TYPE_CHECKING constance
        from configuration.app_settings.constants_settings import ConstanceSettings

        constance: ConstanceSettings = ConstanceSettings()

    @property
    def namespace(self) -> str:  # noqa: N802
        """
        Kubernetes namespace.

        Эта функция читает неймспейс пода из файла, если он существует

        Если файл не найден, вернет 'UNKNOWN'.

        :return: namespace string.
        """
        namespace_file = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
        if namespace_file.exists():
            return namespace_file.read_text().strip()
        return "UNKNOWN"

    def print_all_env_variables(self):
        """Вывести все названия переменных окружения."""
        envs = self._get_all_env_variables(self)
        logger.info("\n" + json.dumps(envs, indent=4))  # noqa: WPS336

    def _get_all_env_variables(self, settings_model: BaseSettings) -> dict[str, Any]:
        """
        Получить все названия переменных окружения.

        :param settings_model: объект настроек.
        :return: словарь. ключ - имя, значение - переменная окружения
        """
        envs = {}
        prefix = settings_model.model_config["env_prefix"]
        for key in settings_model.model_fields.keys():
            if isinstance(getattr(settings_model, key), BaseSettings):
                envs[key] = self._get_all_env_variables(getattr(settings_model, key))
            else:
                envs[key] = f"{prefix}{key.upper()}"  # type: ignore
        return envs


settings: Settings = Settings()
