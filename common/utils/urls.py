import datetime
from decimal import Decimal
from urllib import parse as urllib_parse

from common.errors.exceptions import CustomUnicodeDecodeError


def replace_query_param(url, key, val):  # noqa: WPS110, WPS210
    """
    Заменяет параметр запроса.

    Учитывая URL и пару ключ/значение, устанавливает или заменяет элемент в
    параметрах запроса URL и возвращает новый URL.

    :param url: url string
    :param key: key
    :param val: value
    :return: string
    """
    (scheme, netloc, path, query, fragment) = urllib_parse.urlsplit(  # noqa: WPS236
        force_str(url),
    )
    query_dict = urllib_parse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = urllib_parse.urlencode(sorted(query_dict.items()), doseq=True)
    return urllib_parse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):  # noqa: WPS210
    """
    Удалить элемент в запросе и вернуть новый URL-адрес.

    Учитывая URL-адрес и пару ключей, удалите элемент в параметрах запроса
    URL-адреса и верните новый URL-адрес.

    :param url: url string
    :param key: key
    :return: string
    """
    (scheme, netloc, path, query, fragment) = urllib_parse.urlsplit(  # noqa: WPS236
        force_str(url),
    )
    query_dict = urllib_parse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = urllib_parse.urlencode(sorted(query_dict.items()), doseq=True)
    return urllib_parse.urlunsplit((scheme, netloc, path, query, fragment))


def force_str(string_line, encoding="utf-8", strings_only=False, errors="strict"):
    """
    Конвертирует объект в строку.

    Подобно функции smart_str(), но в отличие от нее ленивые объекты
    разрешаются в строки, а не сохраняются в ленивом состоянии.

    Если strings_only установлено в True, то не конвертировать
    (некоторые) объекты, не являющиеся строками.

    :param string_line: Строка или объект для преобразования в строку.
    :param encoding: Тип кодировки (по умолчанию "utf-8").
    :param strings_only: Если True, то не конвертировать некоторые
        объекты, не являющиеся строками.
    :param errors: Тип ошибки (по умолчанию "strict").
    :raises CustomUnicodeDecodeError: Ошибка декодирования Unicode.
    :return: string.
    """
    if issubclass(type(string_line), str):
        return string_line
    if strings_only and is_protected_type(string_line):
        return string_line
    try:
        if isinstance(string_line, bytes):
            string_line = str(string_line, encoding, errors)
        else:
            string_line = str(string_line)
    except UnicodeDecodeError as exc:
        raise CustomUnicodeDecodeError(string_line, *exc.args)
    return string_line


_PROTECTED_TYPES = (
    type(None),
    int,
    float,
    Decimal,
    datetime.datetime,
    datetime.date,
    datetime.time,
)


def is_protected_type(obj):  # noqa: WPS110
    """
    Определить, является ли экземпляр объекта защищенным типом.

    Объекты защищенных типов сохраняются в исходном виде, когда передаются в
    функцию force_str(strings_only=True).

    :param obj: Объект для проверки.
    :return: boolean.
    """
    return isinstance(obj, _PROTECTED_TYPES)
