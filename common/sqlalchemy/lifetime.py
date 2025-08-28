from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from common.sqlalchemy.sqlalchemy_db_health import sqlalchemy_db_health

from configuration.settings import settings


async def close_engine(sqlalchemy_engine: AsyncEngine) -> None:
    """
    Закрывает соединение с БД.

    :param engine: экземпляр :class:`_asyncio.AsyncEngine`
    """
    await sqlalchemy_engine.dispose()


async def setup_sqlalchemy_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.sqlalchemy_db.url,
        echo=settings.sqlalchemy_db.echo,
        echo_pool=settings.sqlalchemy_db.echo_pool,
        pool_size=settings.sqlalchemy_db.pool_size,
        max_overflow=settings.sqlalchemy_db.max_overflow,
    )
    await sqlalchemy_db_health(engine)
    return engine
