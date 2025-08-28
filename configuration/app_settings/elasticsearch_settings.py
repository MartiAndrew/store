from pydantic_settings import BaseSettings, SettingsConfigDict

from common.utils.paths import PROJECT_ROOT

from configuration.constants import ENV_PREFIX


class ElasticsearchSettings(BaseSettings):
    """Настройки S3."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}S3_",
        env_file=PROJECT_ROOT.joinpath(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    elasticsearch_host: str = "elastic-kino.dev.ritm.site"
    elasticsearch_port: int = 9200
    elasticsearch_user: str = "user"
    elasticsearch_password: str = "password"

    elasticsearch_search_result_size: int = 10
    elasticsearch_rutube_filmach_index: str = ""

    @property
    def elasticsearch_url(self) -> str:
        return (
            f"http://{self.elasticsearch_user}:"
            f"{self.elasticsearch_password}@{self.elasticsearch_host}:{self.elasticsearch_port}"
        )
