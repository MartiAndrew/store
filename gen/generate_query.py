from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from common.utils.paths import PROJECT_ROOT

from configuration.constants import SERVICE_NAME_LOWER


@click.command()
@click.argument("client")
@click.argument("filename")
@click.argument("return_type")
def query(client, filename: str, return_type: str):
    """
    Создать новый запрос.

    :param client: Сервис, для которого генерить запрос.
        service_db, antares_db, etc...
        В папку с таким именем будет положен запрос.

    :param filename: Имя запроса

    :param return_type: none | fetchall | fetchone
    """
    environment = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        keep_trailing_newline=True,
        autoescape=select_autoescape(),
    )
    handler_content = environment.get_template("tmpl/sql_query.jinja2").render(
        filename=filename,
        return_type=return_type,
        client=client,
    )
    new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/db/{client}")
    with open(new_filepath.joinpath(f"queries/{filename}.py"), "w") as new_query:
        new_query.write(handler_content)
    with open(new_filepath.joinpath(f"sql/{filename}.sql"), "w") as new_sql:
        new_sql.write("SELECT 1;")


if __name__ == "__main__":
    query()
