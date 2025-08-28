from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import ENV_PREFIX, SERVICE_NAME_LOWER


class ServiceDbSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}SERVICEDB_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: types.VaultPostgresStr = types.VaultPostgresStr("localhost")
    port: types.VaultPostgresInt = types.VaultPostgresInt(5432)  # noqa: WPS432
    user: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    password: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    # Имя базы данных
    base_name: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    pool_min_size: int = 1
    pool_max_size: int = 5
    pool_max_lifetime: float = 1500.0
    connection_timeout: float = 1.0
    command_retries: int = 3

    @property
    def url(self) -> URL:
        """
        Собрать URL до БД из настроек.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            path=f"/{self.base_name}",
        )
