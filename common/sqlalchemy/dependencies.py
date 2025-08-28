from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.requests import Request

from configuration.settings import settings


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Получает сессию из контекста приложения.

    :param request: current request.
    """
    engine: AsyncEngine = request.app.state.sqlalchemy_engine
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=settings.sqlalchemy_db.expire_on_commit,
        autoflush=settings.sqlalchemy_db.autoflush,
        autocommit=settings.sqlalchemy_db.autocommit,
    )
    async with session_factory() as session:
        yield session
