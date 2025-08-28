from pathlib import Path

import click

from common.utils.paths import PROJECT_ROOT

from configuration.constants import SERVICE_NAME_LOWER


@click.command()
@click.argument("private_type")
@click.argument("url")
@click.argument("method")
def api(private_type: str, url: str, method: str):  # noqa: WPS210
    """
    Создать новую ручку.

    :param private_type: Тип приватности (internal, public)

    :param url: url нового хендлера. Не надо указывать префикс
        /api/internal или /api/<service>/public, только то, что далее.

    :param method: метод хендлера (get, post, etc).
    """
    method = method.lower()
    if not url.startswith("/"):
        url = f"/{url}"
    template_path = Path(__file__).parent.joinpath("tmpl/api_handler.pytemplate")
    with open(template_path, "r") as template_file:
        handler_content = template_file.read()
        handler_content = handler_content.replace("place_project", SERVICE_NAME_LOWER)
        handler_content = handler_content.replace("place_api_type", private_type)
        handler_content = handler_content.replace("place_method", method)
        handler_content = handler_content.replace("place_url", url)
    new_filename = url[1:]
    if url.endswith("/"):
        new_filename = new_filename[:-1]
    new_filename = new_filename.replace("/", "_").replace("-", "_")
    new_filename = new_filename.replace("{", "").replace("}", "")
    new_filename = f"api_{private_type}_{new_filename}_{method}.py"
    new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/web/api/{private_type}")
    new_filepath = new_filepath.joinpath(new_filename)
    with open(new_filepath, "w") as new_handler:
        new_handler.write(handler_content)

    test_template_path = Path(__file__).parent.joinpath(
        "tmpl/test_api_handler.pytemplate",
    )
    with open(test_template_path, "r") as test_template_file:
        test_content = test_template_file.read()
        test_content = test_content.replace("place_project", SERVICE_NAME_LOWER)
        test_content = test_content.replace(
            "place_filename",
            new_filename[:-3],
        )
        test_content = test_content.replace("place_api_type", private_type)
        test_content = test_content.replace("place_method", method)
        test_content = test_content.replace("place_url", url)
    new_filename_test = f"test_{new_filename}"
    new_filepath_test = PROJECT_ROOT.joinpath(
        f"{SERVICE_NAME_LOWER}/tests/test_web/test_api/test_{private_type}",
    )
    new_filepath_test = new_filepath_test.joinpath(new_filename_test)
    with open(new_filepath_test, "w") as new_handler_test:
        new_handler_test.write(test_content)


if __name__ == "__main__":
    api()
