from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from apps.core.settings import settings


class DBDependency:
    def __init__(self) -> None:
        self._engine = create_async_engine(url=settings.db_url, echo=settings.db_echo)
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, autocommit=False
        )

    async def get_session(self):
        session = self._session_factory()
        return session
