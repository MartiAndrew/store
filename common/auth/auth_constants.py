from enum import Enum
from typing import Any

ACCESS_TOKEN_TYPE = "access"  # noqa: S105


class Language(Enum):
    """Языки пользователей."""

    ru = "ru-RU"
    en = "en-IN"

    @classmethod
    def _missing_(cls, lang_value: Any) -> "Language":  # noqa: WPS120
        if isinstance(lang_value, str):
            if lang_value.lower() == cls.en.value.lower():
                return cls.en
        if lang_value is None:
            return cls.ru
        return cls.ru
