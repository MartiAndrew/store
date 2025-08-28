import asyncio
import socket
import threading
from socketserver import ThreadingMixIn
from typing import Callable
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

from loguru import logger

from common.base_workers.types import SupportsWorkerClientState


def _get_best_family(address, port):
    """
    Автоматический выбор family в зависимости от адреса.

    :param address: Host
    :param port: Port
    :return: socket info
    """
    # HTTPServer defaults to AF_INET, which will not start properly if
    # binding an ipv6 address is requested.
    # This function is based on what upstream python did for http_client.server
    # in https://github.com/python/cpython/pull/11767
    infos = socket.getaddrinfo(address, port)
    family, _, _, _, sockaddr = next(iter(infos))  # noqa: WPS236
    return family, sockaddr[0]


def _bake_output(state: SupportsWorkerClientState):
    """
    Ручка health. Проверяет состояние подключенных в воркере клиентов.

    :param state: Worker State
    :return: HTTP Response
    """
    # Choose the correct plain text format of the output.
    errors = asyncio.run(state.health())
    if errors:
        logger.error(f"health check error {errors}")
        return "500 Internal Server Error", [], b""
    return "200 OK", [], b""


def make_wsgi_app(state: SupportsWorkerClientState) -> Callable:
    """
    Создает WSGI app для ручки health.

    :param state: Worker state
    :return: app
    """

    def prometheus_app(environ, start_response):  # noqa: WPS430
        if environ["PATH_INFO"] == "/health":
            status, headers, output = _bake_output(state)
        else:
            status = "200 OK"
            headers = []
            output = b""
        start_response(status, headers)
        return [output]

    return prometheus_app


class _SilentHandler(WSGIRequestHandler):
    """WSGI ручка без логов."""

    def log_message(self, format, *args):  # noqa: WPS125
        """
        Не логировать.

        :param format: log format
        :param args: args
        """


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Тред реквестов HTTP сервера."""

    # Make worker threads "fire and forget". Beginning with Python 3.7 this
    # prevents a memory leak because ``ThreadingMixIn`` starts to gather all
    # non-daemon threads in a list in order to join on them at server close.
    daemon_threads = True


def start_wsgi_server(
    state: SupportsWorkerClientState,
    port: int,
    addr: str = "0.0.0.0",  # noqa: C812, S104
) -> None:
    """
    Запуск WSGI server для проверки health.

    :param state: Worker State
    :param port: Port
    :param addr: Host
    """

    class TmpServer(ThreadingWSGIServer):
        """Копирование ThreadingWSGIServer для обновления address_family."""

    address_family, addr = _get_best_family(addr, port)
    TmpServer.address_family = address_family
    app = make_wsgi_app(state)
    httpd = make_server(addr, port, app, TmpServer, handler_class=WSGIRequestHandler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
