from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import ENV_PREFIX, SERVICE_NAME_LOWER


class SQLAlchemyDbSettings(BaseSettings):
    """Настройки SQLAlchemy."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}SQLALCHEMY_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: types.VaultPostgresStr = types.VaultPostgresStr("localhost")
    port: types.VaultPostgresInt = types.VaultPostgresInt(5432)  # noqa: WPS432
    user: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    password: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    base_name: types.VaultPostgresStr = types.VaultPostgresStr(SERVICE_NAME_LOWER)
    echo: bool = True
    echo_pool: bool = True
    pool_size: int = 5
    max_overflow: int = 10
    expire_on_commit: bool = False
    autoflush: bool = False
    autocommit: bool = False
    connection_timeout: float = 1.0
    command_retries: int = 3

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        """
        Собрать URL SQLAlchemy до БД из настроек.

        :return: database str URL.
        """
        return str(
            URL.build(
                scheme="postgresql+psycopg",
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                path=f"/{self.base_name}",
            )
        )
