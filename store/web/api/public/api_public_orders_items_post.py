from fastapi import Depends, Path
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt
from starlette import status
from starlette.responses import Response

from store.db.service_db.queries.add_item_to_order import AddItemToOrderDbQuery
from store.web.api.public.router import public_router


class AddOrderItemRequest(BaseModel):
    """Тело запроса при добавлении товара в заказ."""

    product_id: NonNegativeInt = Field(..., title="Идентификатор товара")
    quantity: NonNegativeInt = Field(..., title="Количество товара")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "product_id": 1,
                    "quantity": 1,
                },
            ],
        },
    )


class AddOrderItemResponse(BaseModel):
    """Модель ответа при добавлении товара в заказ."""

    order_id: NonNegativeInt = Field(..., title="Идентификатор заказа")
    product_id: NonNegativeInt = Field(..., title="Идентификатор товара")
    order_quantity: NonNegativeInt = Field(
        ...,
        title="Новое количество товара в заказе",
    )


@public_router.post(
    "/orders/{order_id}/items",
    responses={
        status.HTTP_200_OK: {
            "description": "Инкрементирование количества товара.",
            "model": AddOrderItemResponse,
            "content": {
                "application/json": {
                    "example": {
                        "order_id": 1,
                        "product_id": 1,
                        "order_quantity": 2,
                    },
                },
            },
        },
        status.HTTP_201_CREATED: {
            "description": "Добавлен товар в заказ.",
            "model": AddOrderItemResponse,
            "content": {
                "application/json": {
                    "example": {
                        "order_id": 1,
                        "product_id": 1,
                        "order_quantity": 1,
                    },
                },
            },
        },
    },
)
async def add_order_item(
    response: Response,
    request_body: AddOrderItemRequest,
    order_id: NonNegativeInt = Path(..., title="Идентификатор заказа"),
    order_db_query: AddItemToOrderDbQuery = Depends(),
) -> AddOrderItemResponse:
    """
    Метод добавления товара в заказ.

    Метод публичный. В идеале требует авторизации пользователя (должна проходить проверка).
    Реализует добавление товара в заказ. Если товар уже есть в заказе, то увеличивает количество.
    При этом мы проверяем наличие товара. И выбрасываем ошибку, если товара нет в наличии.
    Так же проверяется наличие целостности базы данных.(Если заказ не найден, то выбрасывается ошибка).
    (В реальных условиях проверка целостности не нужна, так как и товар и заказ уже будут в наличии).
    :param response: Response.
    :param order_id: Идентификатор заказа.
    :param request_body: Данные запроса (тело запроса).
    :param order_db_query: Объект запроса к БД.
    :returns: Возвращает AddOrderItemResponse
    """
    result_add_item = await order_db_query(
        order_id=order_id,
        product_id=request_body.product_id,
        quantity=request_body.quantity,
    )
    logger.info(
        f"Добавлен товар ID: {result_add_item.product_id} в заказ ID: {order_id}. "
        f"Количество в заказе: {result_add_item.order_quantity}",
    )
    if result_add_item.order_quantity == request_body.quantity:
        response.status_code = status.HTTP_201_CREATED
        return AddOrderItemResponse(
            order_id=order_id,
            product_id=result_add_item.product_id,
            order_quantity=result_add_item.order_quantity,
        )
    response.status_code = status.HTTP_200_OK
    return AddOrderItemResponse(
        order_id=order_id,
        product_id=result_add_item.product_id,
        order_quantity=result_add_item.order_quantity,
    )
