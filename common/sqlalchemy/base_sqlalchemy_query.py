from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.sqlalchemy.dependencies import get_db_session


class BaseSQLAlchemyQuery:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        """Конструктор базового класса запросов SQLAlchemy."""
        self.session = session
