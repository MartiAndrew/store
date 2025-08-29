INSERT INTO order_item (order_id, product_id, quantity)
VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
ON CONFLICT (order_id, product_id)
DO UPDATE SET quantity = order_item.quantity + excluded.quantity
RETURNING product_id, quantity AS order_quantity
