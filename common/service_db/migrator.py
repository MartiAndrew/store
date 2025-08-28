import datetime
import os
import time
from importlib import import_module

import click
import psycopg
from loguru import logger
from psycopg.errors import UndefinedTable

from configuration.constants import MIGRATION_MODULE, MIGRATION_PATH
from configuration.settings import settings

DEFAULT_MIGRATION_FILE = """def upgrade(cur):
    cur.execute(\"\"\"

    \"\"\")


def downgrade(cur):
    cur.execute(\"\"\"

    \"\"\")
"""


@click.group()
def migrate():
    """Группировка команд миграций для click."""


@click.command()
@click.argument("name")
def create(name):
    """
    Создать новую миграцию.

    :param name: имя миграции.
    """
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{name}.py"
    click.echo(f"Creating new migration file {filename}")
    os_path = MIGRATION_PATH.joinpath(filename)
    with open(os_path, "w") as new_migr_file:
        new_migr_file.write(DEFAULT_MIGRATION_FILE)


@click.command()
def downgrade():
    """Отменить последнюю примененную миграцию."""
    with psycopg.connect(conninfo=str(settings.service_db.url)) as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                cur.execute(
                    "SELECT name, count(*) OVER() FROM migrations "
                    "GROUP BY name ORDER BY name DESC LIMIT 1;",
                )
                fetch = cur.fetchone()
                if not fetch:
                    click.echo("Шутки шутить вздумал?")
                    click.echo("Нельзя откатывать не накатив.")
                    return
                if fetch[1] == 1:
                    click.echo("Шутки шутить вздумал?")
                    click.echo("Нельзя откатывать первую миграцию.")
                    return
                filename = fetch[0]
                click.echo(f"running downgrade migration file {filename}")
                migration_module = _import_migration_from_filename(filename)
                migration_module.downgrade(cur)
                cur.execute(
                    "DELETE FROM migrations WHERE migrations.name = %s;",
                    (filename,),
                )


def func_upgrade(db_url: str):  # noqa: WPS210
    """
    Применить все непримененные миграции.

    :param db_url: URL до БД.
    """
    click.echo("running migrations")
    with psycopg.connect(conninfo=db_url) as sel_conn:
        with sel_conn.cursor() as sel_cur:
            try:
                sel_cur.execute("SELECT name FROM migrations;")
                migrated_filenames = {row[0] for row in sel_cur.fetchall()}
            except UndefinedTable:
                migrated_filenames = set()
    logger.debug(f"applyed migrations {migrated_filenames}")
    with psycopg.connect(conninfo=db_url) as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                filenames_to_migrate_set = _all_migration_files() - migrated_filenames
                if not filenames_to_migrate_set:
                    click.echo("Nothing to migrate")
                filenames_to_migrate = sorted(filenames_to_migrate_set)
                for filename in filenames_to_migrate:
                    click.echo(f"running upgrade migration file {filename}")
                    migration_module = _import_migration_from_filename(filename)
                    migration_module.upgrade(cur)
                    cur.execute(
                        "INSERT INTO migrations VALUES (%s);",
                        (filename,),
                    )


@click.command()
def upgrade():
    """Применить все непримененные миграции."""
    func_upgrade(str(settings.service_db.url))


migrate.add_command(create)
migrate.add_command(upgrade)
migrate.add_command(downgrade)


def _import_migration_from_filename(filename):
    if ".py" in filename:
        filename = filename[:-3]
    return import_module(f".{filename}", MIGRATION_MODULE)


def _all_migration_files():
    listdir = os.listdir(MIGRATION_PATH)
    files = set()
    for os_obj in listdir:
        if not os_obj.endswith(".py") or os_obj == "__init__.py":
            continue
        files.add(os_obj)
    return files


if __name__ == "__main__":
    migrate()
