import re
from typing import Any, Callable, Optional

from fastapi import Depends, Request
from fastapi_localization import LazyString, lazy_gettext
from fastapi_localization.localization import get_gettext

from common.utils.translations import get_translation_catalog

from configuration.settings import settings


def get_locales() -> dict[str, Callable[..., Any]]:
    """
    Вернуть возможные локали приложения.

    :return: Локали.
    """
    return {
        settings.locale.default_locale: get_gettext(
            settings.locale.domain,
            get_translation_catalog(),
            settings.locale.default_locale,
        ),
        settings.locale.eng_locale: get_gettext(
            settings.locale.domain,
            get_translation_catalog(),
            settings.locale.eng_locale,
        ),
    }


def get_accept_language(request: Request) -> Optional[str]:
    """
    Получить значение хедера Accept_Language.

    :param request: Запрос
    :return: Значение хедера
    """
    return request.headers.get("accept-language")


def parse_accept_language(
    accept_language: Optional[str] = Depends(get_accept_language),
) -> tuple[Optional[str], Optional[str]]:
    """
    Достает из заголовка Accept-Language язык и код страны.

    :param accept_language: Значение хедера
    :return: Код языка и страны
    """
    if accept_language:
        if match := re.search(r"(^\w{2,3})-(\w{2,3})", accept_language):
            return match.groups()  # type: ignore

    return None, None


def locale_gettext(request: Request) -> Callable[[str], LazyString]:
    """Получить функцию перевода в зависимости от кода страны.

    :param request: Запрос.
    :returns: Функция перевода.
    """
    _, country_code = parse_accept_language(get_accept_language(request))
    lang_key = (
        settings.locale.eng_locale
        if country_code in settings.locale.eng_list_country_code
        else settings.locale.default_locale
    )
    return request.app.state.locales_gettext.get(lang_key, lazy_gettext)
