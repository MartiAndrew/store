import os
from pathlib import Path

import click
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from common.utils.paths import PROJECT_ROOT

from configuration.constants import SERVICE_NAME_LOWER


def _generate_settings(worker_name, worker_base_path, jinja_env):
    handler_content = jinja_env.get_template("tmpl/worker_settings.jinja2").render(
        worker_name=worker_name,
    )
    new_filepath = worker_base_path.joinpath(f"{worker_name}_settings.py")
    with open(new_filepath, "w") as new_settings:
        new_settings.write(handler_content)


def _generate_worker(worker_name, worker_base_path, jinja_env):
    handler_content = jinja_env.get_template("tmpl/worker.jinja2").render(
        worker_name=worker_name,
    )
    new_filepath = worker_base_path.joinpath(f"{worker_name}.py")
    with open(new_filepath, "w") as new_worker:
        new_worker.write(handler_content)


def _generate_deploy_values(worker_name):
    new_worker_deploy = {
        worker_name: {
            "containers": {
                worker_name: {
                    "args": [
                        f"{SERVICE_NAME_LOWER}/workers/{worker_name}/{worker_name}.py",
                    ],
                    "services": {},
                },
            },
            "enabled": True,
            "replicaCount": 1,
        },
    }
    val_path = PROJECT_ROOT.joinpath(
        f"deploy/charts/{SERVICE_NAME_LOWER}-workers/values.yaml",
    )
    with open(val_path, "r") as values_read_file:
        values_yaml = yaml.safe_load(values_read_file)
        values_yaml["apps"].update(new_worker_deploy)
    with open(val_path, "w") as values_write_file:
        yaml.safe_dump(values_yaml, values_write_file)


def _generate_base_worker_test():
    worker_tests_path = PROJECT_ROOT.joinpath(
        f"{SERVICE_NAME_LOWER}/tests/test_workers/test_base_worker.py",
    )
    if not os.path.exists(worker_tests_path):
        tmpl = Path(__file__).parent.joinpath("tmpl/test_base_worker.pytemplate")
        with open(tmpl, "r") as tmpl_file:
            with open(worker_tests_path, "w") as new_test:
                new_test.write(tmpl_file.read())


def _generate_worker_test(worker_name, jinja_env):
    test_content = jinja_env.get_template("tmpl/test_worker.jinja2").render(
        worker_name=worker_name,
        service=SERVICE_NAME_LOWER,
    )
    new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/tests/test_workers")
    with open(new_filepath.joinpath(f"test_{worker_name}.py"), "w") as new_test:
        new_test.write(test_content)


def _add_worker_to_settings(worker_name: str):  # noqa: WPS210
    w_class = "".join([word.capitalize() for word in worker_name.split("_")])
    w_str = f"\n    {worker_name}: {w_class}Settings = {w_class}Settings()"
    w_import_str = (
        f"\nfrom {SERVICE_NAME_LOWER}.workers.{worker_name}.{worker_name}_settings "
        f"import {w_class}Settings"
    )
    settings_path = PROJECT_ROOT.joinpath("configuration/settings.py")
    with open(settings_path, "r") as settings_read_file:
        cont = settings_read_file.read()
    find_phrase = "# Не удалять строчку, по ней идет поиск"
    cont = cont.replace(find_phrase, f"{find_phrase}{w_str}")
    find_import_phrase = (
        "from configuration.constants import ENV_PREFIX, SERVICE_NAME_LOWER"
    )
    cont = cont.replace(find_import_phrase, f"{find_import_phrase}{w_import_str}")
    with open(settings_path, "w") as settings_write_file:
        settings_write_file.write(cont)


@click.command()
@click.argument("worker_name")
def worker(worker_name: str):  # noqa: WPS210
    """
    Создать новый воркер.

    :param worker_name: Название воркера.
    """
    environment = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        keep_trailing_newline=True,
        autoescape=select_autoescape(),
    )
    worker_base_path = PROJECT_ROOT.joinpath(
        f"{SERVICE_NAME_LOWER}/workers/{worker_name}",
    )
    worker_base_path.mkdir(parents=False, exist_ok=False)
    with open(worker_base_path.joinpath("__init__.py"), "w") as init_file:
        init_file.write(f'"""Воркер {worker_name}."""\n')
    _generate_settings(worker_name, worker_base_path, environment)
    _generate_worker(worker_name, worker_base_path, environment)
    _generate_deploy_values(worker_name)
    _add_worker_to_settings(worker_name)
    _generate_base_worker_test()
    _generate_worker_test(worker_name, environment)


if __name__ == "__main__":
    worker()
