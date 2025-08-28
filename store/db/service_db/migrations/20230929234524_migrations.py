def upgrade(cur):
    cur.execute(
        """
    CREATE TABLE migrations (
        name text
    );
    """,
    )


def downgrade(cur):
    cur.execute("""DROP TABLE migrations;""")
