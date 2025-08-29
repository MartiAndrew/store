UPDATE product
SET quantity = quantity - %(quantity)s
WHERE id = %(product_id)s;
