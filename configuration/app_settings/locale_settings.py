from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class LocaleSettings(BaseSettings):
    """Настройки конфигов."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}LOCALES_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    domain: str = "base"
    default_locale: str = "ru"
    eng_locale: str = "en"

    @property
    def eng_list_country_code(self) -> tuple[str, ...]:
        """
        Возвращает список локалей для английского языка.

        :return: списк локалей
        """
        return ("IN",)
