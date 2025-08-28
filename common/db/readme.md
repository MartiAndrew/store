Внедрение ОРМ
=============

```
poetry add tortoise-orm --extras psycopg
```

в web/lifetime.py в register_startup_event() добавить
```python
from tortoise import Tortoise, connections

await Tortoise.init(
        db_url=str(settings.service_db.url).replace("postgresql://", "psycopg://"),
        modules={'models': ['projectname.db.service_db.orm.models']}
    )
    await connections.close_all()
```
Сразу закрываем коннекты, т.к. ОРМ у нас только для формирования запросов.

Если ОРМ для антареса. то поменять service_db на antares_db

В register_shutdown_event() добавить  ```await connections.close_all()```

Теперь можно в PROJECTNAME/db/service_db/orm/models.py добавить стандартную модельку

```python
from tortoise.models import Model
from tortoise import fields

class Users(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    telegram_nick = fields.TextField()
    email = fields.TextField()

    def __str__(self):
        return self.name

```


Тогда в ручке (или где надо получить данные) можно делать так:

```python
async def get_users(
    db: AsyncConnectionPool = Depends(get_service_db_pool),
) -> HandlerResponse:
    raw_sql = Users.filter(name__startswith="Головач").sql()
    logger.info(f"Tortoise SQL: {raw_sql}")
    async with cursor_manager(db_pool=db, db_connection_timeout=5.0) as cursor:
        await cursor.execute(raw_sql)
        raw_result = await cursor.fetchall()
        logger.info(raw_result)
```
