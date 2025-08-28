# Список доступных клиентов

* [service_db]( #service_db) - клиент для собственной БД проекта
* [taskiq](#taskiq) - Подключение taskiq


# Клиенты

## <a id="service_db"></a>Service DB
### Подключение
В файл configuration/settings.py добавить

```python
from configuration.app_settings.service_db_settings import ServiceDbSettings

...
service_db: ServiceDbSettings = ServiceDbSettings()
```
В файл web/lifetime.py добавить
```python
from common.service_db.lifetime import setup_service_db, stop_service_db

...
def register_startup_event(
    ...
    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        await setup_service_db(app)
        ...
    async def _shutdown() -> None:  # noqa: WPS430
        await stop_service_db(app)
```
В файл web/api/monitoring/api_health.py добавить
```python
from common.service_db.service_db_health import service_db_health
async def test_health(
    ...
    service_db_pool: AsyncConnectionPool,
) -> None:
...
    errors.update(await service_db_health(request))
```

## <a id="taskiq"></a>Taskiq
### Подключение
В файл configuration/settings.py добавить
```python
from common.service_db.taskiq_settings import TaskiqSettings
...
    taskiq: TaskiqSettings = TaskiqSettings()
```
В файл web/lifetime.py добавить
```python
from common.taskiq.lifetime import setup_taskiq, stop_taskiq

...
def register_startup_event(
    ...
    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        await setup_taskiq()
        ...
    async def _shutdown() -> None:  # noqa: WPS430
        await stop_taskiq()
```
Сгенерировать таску (имя всегда должно начинаться с task_)
```bash
python ./gen/generate.py task task_name
```
Для вызова таски необходим параметр LogData.
В АПИ части он добавляется автоматически в LoggerMiddleware в app.state.log_data

Вызов таски в таком случае будет примерно таким
```python
from starlette.requests import Request

from <service_name>.tasks.task_name import task_name

async def api_handler(request: Request):
    await task_name.kiq(log_data=request.app.state.log_data)
```


### Описание
Предоставляет фикстуру ```service_db_pool```

Предоставляет dependency ```get_service_db_pool```

### Описание генераторов:
- [Generators](../gen/readme.md)
