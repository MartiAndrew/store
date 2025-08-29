from pathlib import Path

from psycopg.errors import ForeignKeyViolation
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field, NonNegativeInt, TypeAdapter

from common.service_db.base_service_db_queries import BaseServiceDbQuery

from store.web.exceptions import OrderCheckViolationError, OrderNotFoundError

SQL_ADD_ITEM_TO_ORDER = (
    Path(__file__)
    .parent.parent.joinpath(
        "sql/add_item_to_order.sql",
    )
    .read_text()
)

SQL_UPDATE_PRODUCT = (
    Path(__file__)
    .parent.parent.joinpath(
        "sql/update_product_quantity.sql",
    )
    .read_text()
)

SQL_SELECT_FOR_UPDATE_PRODUCT = (
    Path(__file__)
    .parent.parent.joinpath(
        "sql/select_product.sql",
    )
    .read_text()
)


class AddItemToOrderResult(BaseModel):
    """Модель результата изменения состава заказа."""

    product_id: NonNegativeInt = Field(..., title="Идентификатор товара")
    order_quantity: NonNegativeInt = Field(
        ...,
        title="Новое количество товара в заказе",
    )


class AddItemToOrderDbQuery(BaseServiceDbQuery):
    """Класс запроса добавления товара в заказ."""

    async def __call__(  # noqa: WPS238 WPS210
        self,
        order_id: int,
        product_id: int,
        quantity: int,
    ) -> AddItemToOrderResult:
        """
        Транзакционный запрос на добавления товара в заказ.

        Выполняется несколько SQL-запросов:
        1. Проверка наличия товара и блокировка строки продукта для дальнейшего изменения.
        2. Обновление количества товара на складе.
        3. Добавление товара в заказ или увеличение его количества.
        Проверка наличия товара и его обновление делается отдельными запросами без CTE для возможности
        внесения дополнителоьной бизнес логики в дальнейшем.
        :param order_id: Идентификатор заказа.
        :param product_id: Идентификатор товара.
        :param quantity: Количество товара.
        :raises TypeError: Если тип db не валиден.
        :raises OrderNotFoundError: Если заказ не найден (ошибка целостности БД).
        :raises OrderCheckViolationError: Если данные по продукту не соответствуют требованиям.
        :return: объект результата изменения состава заказа AddItemToOrderResult или None
        """
        query_upsert_params = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
        }
        query_product_params = {
            "product_id": product_id,
            "quantity": quantity,
        }

        if not isinstance(self.db, AsyncConnectionPool):
            raise TypeError("Тип db не валиден.")
        async with self.db.connection() as conn:
            async with conn.transaction():
                async with conn.cursor(  # type: ignore
                    binary=True,
                    row_factory=dict_row,
                ) as cursor:
                    await cursor.execute(
                        SQL_SELECT_FOR_UPDATE_PRODUCT,
                        query_product_params,
                    )
                    if not await cursor.fetchone():
                        raise OrderCheckViolationError

                    await cursor.execute(SQL_UPDATE_PRODUCT, query_product_params)

                    try:
                        await cursor.execute(SQL_ADD_ITEM_TO_ORDER, query_upsert_params)
                    except ForeignKeyViolation as exc:
                        if exc.diag.constraint_name == "order_item_order_id_fkey":
                            raise OrderNotFoundError
                    raw_result = await cursor.fetchone()

                    return TypeAdapter(AddItemToOrderResult).validate_python(raw_result)
