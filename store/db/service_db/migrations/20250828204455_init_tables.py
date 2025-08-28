def upgrade(cur):
    cur.execute(
        """
        CREATE TABLE category (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            parent_id INT REFERENCES category(id) ON DELETE CASCADE
        );
        CREATE INDEX idx_category_parent ON category(parent_id);
        CREATE TABLE product (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            quantity INT NOT NULL DEFAULT 0,
            price NUMERIC(12,2) NOT NULL,
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
        CREATE INDEX idx_product_category ON product(category_id); 
        CREATE TABLE client (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address TEXT
        );
        CREATE TABLE customer_order (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            client_id INT NOT NULL REFERENCES client(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX idx_order_client ON customer_order(client_id);
        CREATE TABLE order_item (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id BIGINT NOT NULL REFERENCES customer_order(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
            quantity INT NOT NULL CHECK (quantity > 0),
            price NUMERIC(12,2) NOT NULL
        );
        CREATE UNIQUE INDEX idx_order_item_order_product
        ON order_item(order_id, product_id);
    """,
    )


def downgrade(cur):
    cur.execute(
        """
        DROP TABLE order_item;
        DROP TABLE customer_order;
        DROP TABLE product;
        DROP TABLE category;
        DROP TABLE client;
        """,
    )
