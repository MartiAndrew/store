from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import ENV_PREFIX


class AuthSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}AUTH_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # рубильник проверки токена в кеше токенов
    token_cache_checking: bool = True
    # JWT ключ
    jwt_signing_key: types.VaultLocalStr = types.VaultLocalStr("jwt_signing_key")
