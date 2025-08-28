"""Модуль для работы с мониторингом и метриками приложения."""
from importlib import import_module
from pathlib import Path

for pf in Path(__file__).parent.glob("*.py"):
    module_name = pf.stem
    if not module_name.startswith("_"):
        import_module(f".{module_name}", __package__)
    del pf, module_name  # noqa: WPS420
del import_module, Path  # noqa: WPS420
