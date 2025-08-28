from abc import ABC, abstractmethod


class UrlHTTPSPrefixer(ABC):
    """Абстрактный класс для присолединения протокола https к ссылкам."""

    @abstractmethod
    def url_https_prefixer(self, link: str | None) -> str | None:
        """
        Присоединить протокол https к ссылке.

        :param link: ссылка
        :return: url
        """


class HttpFormatter(UrlHTTPSPrefixer):
    """Базовый класс для присолединения протокола https к ссылкам."""

    LINK_PROTOCOL: str = "https://"

    def url_https_prefixer(self, link: str | None) -> str | None:
        """
        Присоединить протокол https к ссылке.

        :param link: ccылка
        :return: url
        """
        base_protocol = self.LINK_PROTOCOL
        if not link:
            return None
        if link.startswith("http_client://") or link.startswith("https://"):
            return link
        return base_protocol + link
