from starlette.requests import Request

from common.rabbitmq.connection import RabbitConnection


def get_rmq_channel_pool(request: Request) -> RabbitConnection:
    """
    Вернуть пул коннектов к RMQ сервиса.

    :param request: current request.
    :returns: rmq connections pool.
    """
    return request.app.state.clients.rabbitmq_connection
