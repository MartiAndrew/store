SELECT
    id,
    quantity
FROM product
WHERE
    id = %(product_id)s
    AND quantity >= %(quantity)s
FOR UPDATE;
