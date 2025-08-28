import click
from gen.generate_api import api
from gen.generate_client_connect import connect
from gen.generate_query import query
from gen.generate_task import task
from gen.generate_values import values
from gen.generate_worker import worker


@click.group()
def generate():
    """Группировка команд генерации для click."""


generate.add_command(api)
generate.add_command(query)
generate.add_command(values)
generate.add_command(task)
generate.add_command(worker)
generate.add_command(connect)


if __name__ == "__main__":
    generate()
