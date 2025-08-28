from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from common.utils.paths import PROJECT_ROOT

from configuration.constants import SERVICE_NAME_LOWER


def _generate_test(task_name):
    environment = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        keep_trailing_newline=True,
        autoescape=select_autoescape(),
    )
    test_content = environment.get_template("tmpl/test_task.jinja2").render(
        task_name=task_name,
        service=SERVICE_NAME_LOWER,
    )
    new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/tests/test_tasks")
    with open(new_filepath.joinpath(f"test_{task_name}.py"), "w") as new_test:
        new_test.write(test_content)


@click.command()
@click.argument("task_name")
def task(task_name: str):  # noqa: WPS210
    """
    Создать новую taskiq таску.

    :param task_name: Название таски. Должно начинаться с task_*
        Если не начинается, то автоматически добавится к названию.
    """
    if not task_name.startswith("task_"):
        task_name = f"task_{task_name}"
    template_path = Path(__file__).parent.joinpath("tmpl/task.pytemplate")
    with open(template_path, "r") as template_file:
        handler_content = template_file.read()
        handler_content = handler_content.replace("place_task_name", task_name)
    new_filename = f"{task_name}.py"
    new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/tasks/{new_filename}")
    with open(new_filepath, "w") as new_task:
        new_task.write(handler_content)
    click.echo("Не забудь включить таскик в deploy/charts/*-workers/values.yaml")
    _generate_test(task_name)


if __name__ == "__main__":
    task()
