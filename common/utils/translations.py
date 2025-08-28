from pathlib import Path

from common.utils.paths import PROJECT_ROOT


def get_translation_catalog() -> Path:
    """
    Возвращает путь до каталога с переводами.

    :return: полный путь до /locale
    """
    return PROJECT_ROOT.joinpath("locale")
