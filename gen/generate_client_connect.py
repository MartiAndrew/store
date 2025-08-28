import subprocess  # noqa: S404

import click

from common.utils.paths import PROJECT_ROOT

OFFSET = "\n        "

SERVICES_CONFIG = {  # noqa: WPS407
    "service_db": {
        "settings": {
            "import": (
                "\nfrom common.service_db.service_db_settings "
                "import ServiceDbSettings"
            ),
            "init": "\n    service_db: ServiceDbSettings = ServiceDbSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING service_db"
                f"{OFFSET}from common.service_db.service_db_settings "
                "import ServiceDbSettings"
                "\n"
                f"{OFFSET}service_db: ServiceDbSettings = ServiceDbSettings()"
            ),
        },
        "clients": {
            "import": "\nimport psycopg_pool",
            "init": "\n    service_db_pool: psycopg_pool.AsyncConnectionPool",
        },
    },
    "antares_db": {
        "settings": {
            "import": (
                "\nfrom common.antares_db.antares_db_settings "
                "import AntaresDbSettings"
            ),
            "init": "\n    antares_db: AntaresDbSettings = AntaresDbSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING antares_db"
                f"{OFFSET}from common.antares_db.antares_db_settings "
                "import AntaresDbSettings"
                "\n"
                f"{OFFSET}antares_db: AntaresDbSettings = AntaresDbSettings()"
            ),
        },
        "clients": {
            "import": "\nimport psycopg_pool",
            "init": "\n    antares_db_pool: psycopg_pool.AsyncConnectionPool",
        },
    },
    "service_redis": {
        "settings": {
            "import": (
                "\nfrom common.service_redis.service_redis_settings "
                "import ServiceRedisSettings"
            ),
            "init": (
                "\n    service_redis: ServiceRedisSettings = ServiceRedisSettings()"
            ),
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING service_redis"
                f"{OFFSET}from common.service_redis.service_redis_settings "
                "import ServiceRedisSettings"
                "\n"
                f"{OFFSET}service_redis: ServiceRedisSettings = ServiceRedisSettings()"
            ),
        },
        "clients": {
            "import": "\nfrom redis.asyncio import ConnectionPool",
            "init": "\n    service_redis_pool: ConnectionPool",
        },
    },
    "token_cache": {
        "settings": {
            "import": (
                "\nfrom common.token_cache.token_cache_settings "
                "import TokenCacheSettings"
            ),
            "init": "\n    token_cache: TokenCacheSettings = TokenCacheSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING token_cache"
                f"{OFFSET}from common.token_cache.token_cache_settings "
                "import TokenCacheSettings"
                "\n"
                f"{OFFSET}token_cache: TokenCacheSettings = TokenCacheSettings()"
            ),
        },
        "clients": {
            "import": "\nfrom redis.asyncio import ConnectionPool",
            "init": "\n    token_cache_redis_pool: ConnectionPool",
        },
    },
    "constance": {
        "settings": {
            "import": (
                "\nfrom common.constance.constants_settings import ConstanceSettings"
            ),
            "init": "\n    constance: ConstanceSettings = ConstanceSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING constance"
                f"{OFFSET}from common.constance.constants_settings "
                f"import ConstanceSettings"
                "\n"
                f"{OFFSET}constance: ConstanceSettings = ConstanceSettings()"
            ),
        },
        "clients": {
            "import": "\nfrom redis.asyncio import ConnectionPool",
            "init": "\n    constance_pool: ConnectionPool",
        },
    },
    "musica_http": {
        "settings": {
            "import": (
                "\nfrom common.musica_http.musica_settings " "import MusicaSettings"
            ),
            "init": "\n    musica_http: MusicaSettings = MusicaSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING musica_http"
                f"{OFFSET}from common.musica_http.musica_settings import MusicaSettings"
                "\n"
                f"{OFFSET}rabbit: MusicaSettings = MusicaSettings()"
            ),
        },
    },
    "rabbitmq": {
        "settings": {
            "import": (
                "\nfrom common.rabbitmq.rabbitmq_settings " "import RabbitSettings"
            ),
            "init": "\n    rabbit: RabbitSettings = RabbitSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING rabbitmq"
                f"{OFFSET}from common.rabbitmq.rabbitmq_settings import RabbitSettings"
                "\n"
                f"{OFFSET}rabbit: RabbitSettings = RabbitSettings()"
            ),
        },
    },
    "taskiq": {
        "settings": {
            "import": "\nfrom common.taskiq.taskiq_settings import TaskiqSettings",
            "init": "\n    taskiq: TaskiqSettings = TaskiqSettings()",
            "mypy": (
                f"{OFFSET}# TYPE_CHECKING taskiq"
                f"{OFFSET}from common.taskiq.taskiq_settings import TaskiqSettings"
                "\n"
                f"{OFFSET}rabbit: TaskiqSettings = TaskiqSettings()"
            ),
        },
    },
}


def _add_to_file(service_name, file_name):  # noqa: WPS210
    w_settings = SERVICES_CONFIG[service_name].get(file_name)
    if not w_settings:
        return
    w_init_str = w_settings["init"]
    w_import_str = w_settings["import"]
    settings_path = PROJECT_ROOT.joinpath(f"configuration/{file_name}.py")
    with open(settings_path, "r") as settings_read_file:
        cont = settings_read_file.read()
    find_phrase = "# Не удалять строчку, по ней идет поиск"
    cont = cont.replace(find_phrase, f"{find_phrase}{w_init_str}")
    find_import_phrase = "from loguru import logger"
    cont = cont.replace(find_import_phrase, f"{find_import_phrase}{w_import_str}")
    with open(settings_path, "w") as settings_write_file:
        settings_write_file.write(cont)
    subprocess.run(["black", settings_path])  # noqa: S603, S607
    subprocess.run(["isort", settings_path])  # noqa: S603, S607


def _remove_from_settings_type_check(service_name):
    w_settings = SERVICES_CONFIG[service_name].get("settings")
    if not w_settings:
        return
    settings_path = PROJECT_ROOT.joinpath("configuration/settings.py")
    with open(settings_path, "r") as settings_read_file:
        cont = settings_read_file.read()
    cont = cont.replace(w_settings["mypy"], "")
    with open(settings_path, "w") as settings_write_file:
        settings_write_file.write(cont)


def _add_to_settings(service_name: str):
    _add_to_file(service_name, "settings")


def _add_to_clients(service_name: str):
    _add_to_file(service_name, "clients")


@click.command()
@click.argument("service_name")
def connect(service_name: str):  # noqa: WPS210
    """
    Подключить сервис в проект.

    :param service_name: Название сервиса.
    """
    if service_name not in SERVICES_CONFIG.keys():
        click.echo("Сервис не найден")
    _remove_from_settings_type_check(service_name)
    _add_to_settings(service_name)
    _add_to_clients(service_name)


if __name__ == "__main__":
    connect()
