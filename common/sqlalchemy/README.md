# Работа с SQLAlchemy в FastAPI (Async)

Данное руководство описывает конфигурацию и использование SQLAlchemy с асинхронным движком в проекте на FastAPI.

---

## 1. Конфигурация SQLAlchemy через Pydantic

Для настройки подключения используется класс `SQLAlchemyDbSettings`, наследующийся от `pydantic_settings.BaseSettings`. Это позволяет удобно хранить параметры в `.env` и соблюдает принципы 12-факторного приложения.

### Основные поля класса

| Поле              | Назначение                                                                                         |
|-------------------|--------------------------------------------------------------------------------------------------|
| `host`            | Хост базы данных, например `localhost` или `postgres`                                            |
| `port`            | Порт PostgreSQL (по умолчанию 5432)                                                              |
| `user`            | Имя пользователя PostgreSQL                                                                       |
| `password`        | Пароль пользователя PostgreSQL                                                                    |
| `base_name`       | Название базы данных                                                                              |
| `echo`            | Если `True`, SQLAlchemy логирует SQL-запросы (полезно для отладки)                                |
| `echo_pool`       | Логирование операций с пулом соединений                                                          |
| `pool_size`       | Размер пула соединений (по умолчанию 5)                                                          |
| `max_overflow`    | Количество дополнительных соединений, создаваемых сверх пула при нагрузке                         |
| `expire_on_commit`| Управляет автоматическим "истечением" объектов после коммита (лучше ставить `False` в async)     |
| `autoflush`       | Если `True`, SQLAlchemy автоматически вызывает `flush()` перед запросами                          |
| `autocommit`      | В асинхронном режиме рекомендуется `False`                                                       |
| `connection_timeout` | Время ожидания подключения (пока не используется явно)                                         |
| `command_retries` | Количество попыток повторить команду при ошибке (пока не используется явно)                       |
| `naming_convention`| Правила именования SQL-ограничений для Alembic и миграций                                        |

### Свойство `.url`

Метод собирает строку подключения к базе данных в формате:
```python
postgresql+psycopg://user:password@host:port/dbname
```

## 2. Создание асинхронного движка `AsyncEngine`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

async def setup_sqlalchemy_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.sqlalchemy_db.url,
        echo=settings.sqlalchemy_db.echo,
        echo_pool=settings.sqlalchemy_db.echo_pool,
        pool_size=settings.sqlalchemy_db.pool_size,
        max_overflow=settings.sqlalchemy_db.max_overflow,
    )
    await sqlalchemy_db_health(engine)  # Проверка соединения с БД (опционально)
    return engine
```
   * Используется create_async_engine из sqlalchemy.ext.asyncio.

   * Параметры передаются из настроек.

   * Можно включить логирование SQL-запросов и операций с пулом.

## 3. Генератор сессий для FastAPI

```python
    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from typing import AsyncGenerator
    
    async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
        engine = request.app.state.sqlalchemy_engine
        session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=settings.sqlalchemy_db.expire_on_commit,
            autoflush=settings.sqlalchemy_db.autoflush,
            autocommit=settings.sqlalchemy_db.autocommit,
        )
        async with session_factory() as session:
            yield session
```

   * Используется async_sessionmaker для создания фабрики сессий.

   * Сессия асинхронная, создаётся на каждый запрос и закрывается автоматически.

   * В FastAPI можно использовать как зависимость:
```python
    @router.get("/items")
    async def get_items(session: AsyncSession = Depends(get_db_session)):
    ...
```

## 🔁 CRUD-функции (crud.py)

✅ Create

```python
    from models import User
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async def create_user(session: AsyncSession, name: str, email: str) -> User:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
```

🔎 Read

```python
    from sqlalchemy import select
    
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
```

✏️ Update

```python
    from sqlalchemy import update
    
    async def update_user_email(session: AsyncSession, user_id: int, new_email: str) -> None:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=new_email)
        )
        await session.commit()
```

❌ Delete

```python
    from sqlalchemy import delete
    
    async def delete_user(session: AsyncSession, user_id: int) -> None:
        await session.execute(
            delete(User)
            .where(User.id == user_id)
        )
        await session.commit()
```