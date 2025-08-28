from typing import Any, Dict, List, Optional, TypeVar

from fastapi import Request
from pydantic import BaseModel

from common.utils.urls import remove_query_param, replace_query_param

from configuration.constants import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    PAGINATION_MAX_LIMIT,
)

MT = TypeVar("MT", bound=BaseModel)


def _positive_int(
    integer_string: str,
    strict: bool = False,
    cutoff: Optional[int] = None,
) -> int:
    """
    Преобразует строку в положительное число.

    :param integer_string: str
    :param strict: Eсли strict=True 0 считается отрицательным.
    :param cutoff: Максимальное значение.
    :raises ValueError: Если число отрицательное.
    :return: int
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


class CursorPagination:  # noqa: WPS230
    """Кастомный класс пагинатора."""

    page_data: List[MT]  # type: ignore
    max_page_size = PAGINATION_MAX_LIMIT
    default_page_size: int = DEFAULT_PAGE_SIZE
    default_page = 1

    page_query_param = "page"
    page_size_query_param = "page_size"

    def __init__(self, request: Request):
        self.has_next = False
        self.has_previous = False
        self.request = request
        self.page_size = int(
            request.query_params.get(
                self.page_size_query_param,
                self.default_page_size,
            ),
        )
        self.page = int(
            request.query_params.get(
                self.page_query_param,
                self.default_page,
            ),
        )
        self._page_size = self.get_page_size()
        self.page_number = self._get_page_number()
        self.offset = (self.page_number - 1) * self._page_size
        self.limit = self._page_size + 1

    def paginate_queryset(
        self,
        queryset: List[MT],
    ) -> Optional[List[MT]]:
        """
        Метод принимает QuerySet.

        Возвращает список объектоов на запрошенной странице.

        :param queryset: QuerySet
        :return: возвращает список объектоов на запрошенной странице
        """
        if not self._page_size:
            return None

        if not self.page_number:
            self.page_number = 1

        self.page_data = list(queryset[: self._page_size])

        if len(queryset) > len(self.page_data):
            self.has_next = True
        if self.page_number > 1:
            self.has_previous = True

        return self.page_data

    def get_paginated_response(
        self,
        data: Any,  # noqa: WPS110
    ) -> Dict:
        """
        Возвращает response с разбивкой по страницам.

        :param data: Сериализованные данные станицы.
        :return: Response.
        """
        return {
            "count": self._get_count(),
            "next": self._get_next_link(),
            "previous": self._get_previous_link(),
            "results": data,
        }

    def get_page_size(self) -> int:
        """
        Возращает кол-во элементов на страницe.

        :return: кол-во элементов на страницe
        """
        try:
            return _positive_int(
                self.request.query_params.get(
                    self.page_size_query_param,
                    str(self.default_page_size),
                ),
                strict=True,
                cutoff=self.max_page_size,
            )
        except (KeyError, ValueError):
            return self.page_size

    def _get_page_number(self) -> int:
        """
        Возвращает номер страницы из query параметров.

        :return: Возвращает номер страницы или None
        """
        try:
            return _positive_int(
                self.request.query_params.get(
                    self.page_query_param,
                    str(self.default_page),
                ),
                strict=True,
            )
        except (KeyError, ValueError):
            return DEFAULT_PAGE_NUMBER

    def _get_count(self) -> int:
        """
        Вовзращает фейковое QuerySet.count.

        :return: int
        """
        if not self._page_size:
            return 0
        if not self.page_data:
            return 0
        page_number = self.page_number or 1
        count = (page_number - 1) * self._page_size + len(self.page_data)
        if self.has_next:
            count += 1
        return count

    def _get_next_link(self) -> Optional[str]:
        """
        Возвращает ссылку на следующую станицу, если она есть.

        :return: ссылка на следующую станицу или None.
        """
        if not self.has_next:
            return None
        url = self.request.url
        page_number = (self.page_number or 1) + 1
        return replace_query_param(url, self.page_query_param, page_number)

    def _get_previous_link(self) -> Optional[str]:
        """
        Возвращает ссылку на предыдущую станицу, если она есть.

        :return: ссылка на предыдущую станицу или None.
        """
        if not self.has_previous:
            return None
        url = self.request.url
        page_number = (self.page_number or 1) - 1
        if page_number < 2:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
