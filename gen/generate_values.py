import enum
import typing

import click
import yaml
from pydantic_settings import BaseSettings

from common.utils.paths import PROJECT_ROOT

from configuration import types
from configuration.constants import SERVICE_NAME_LOWER
from configuration.settings import settings


def _get_value_place(setting) -> str:
    if setting in {types.VaultLocalStr, types.VaultLocalInt}:
        return "vault_local"
    if setting in {types.VaultPostgresStr, types.VaultPostgresInt}:
        return "vault_postgres"
    if setting in {types.VaultRabbitStr, types.VaultRabbitInt}:
        return "vault_rabbitmq"
    return "values"


def _get_all_env_variables(  # noqa: WPS231, C901
    settings_model: BaseSettings,
) -> dict[str, typing.Any]:
    """
    Получить все названия переменных окружения и по типу их место хранения.

    :param settings_model: Объект настроек
    :return: словарь.
    """
    envs = {}
    obj_types = typing.get_type_hints(settings_model)
    prefix = settings_model.model_config["env_prefix"]
    for key in settings_model.model_fields.keys():
        if key in {"commit_hash", "version", "hostname"}:
            continue
        if isinstance(getattr(settings_model, key), BaseSettings):
            envs.update(_get_all_env_variables(getattr(settings_model, key)))
        else:
            default = getattr(settings_model, key, "")
            if isinstance(default, enum.Enum):
                default = default.value
            if default is None:
                default = "null"
            if not isinstance(default, int | float | bool | str):
                default = str(default)
            elif isinstance(default, bool):
                default = int(default)
            envs[f"{prefix}{key.upper()}"] = {
                "value_type": _get_value_place(obj_types[key]),
                "default": default,
            }
    return envs


def _values(chart_postfix: str):  # noqa: C901, WPS210, WPS231, WPS110
    """
    Синхронизировать values.yaml и settings.

    :param chart_postfix: Постфикс чарта.
        Используется, чтоб можно было генерить values.yaml и для api и для воркеров.
    """
    val_path = PROJECT_ROOT.joinpath(
        f"deploy/charts/{SERVICE_NAME_LOWER}{chart_postfix}/values.yaml",
    )
    envs = _get_all_env_variables(settings)
    with open(val_path, "r") as values_read_file:
        values_yaml = yaml.safe_load(values_read_file)
        env_path = values_yaml["apps"]["_default"]
        env_path = env_path["containers"]["_default"]["env"]
        yaml_values = env_path["local"]
        yaml_local_vault = env_path["vault"]["env"]["local"]
        yaml_postgres_vault = env_path["vault"]["env"]["postgres"]
        yaml_rabbitmq_vault = env_path["vault"]["env"]["rabbitmq"]
    need_write = False
    for env, conf in envs.items():
        if conf["value_type"] == "values":
            if env not in yaml_values.keys():
                yaml_values.update({env: conf["default"]})
                need_write = True
        if conf["value_type"] == "vault_local":
            if env not in yaml_local_vault:
                yaml_local_vault.append(env)
                need_write = True
        if conf["value_type"] == "vault_postgres":
            if env not in yaml_postgres_vault:
                yaml_postgres_vault.append(env)
                need_write = True
        if conf["value_type"] == "vault_rabbitmq":
            if env not in yaml_rabbitmq_vault:
                yaml_rabbitmq_vault.append(env)
                need_write = True
    if need_write:
        max_length_yaml_line = 88
        with open(val_path, "w") as values_write_file:
            yaml.safe_dump(values_yaml, values_write_file, width=max_length_yaml_line)


@click.command()
def values():  # noqa: WPS110
    """Синхронизировать values.yaml и settings."""
    _values("-workers")


if __name__ == "__main__":
    values()
