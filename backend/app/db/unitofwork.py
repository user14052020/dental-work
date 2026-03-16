from __future__ import annotations

from collections.abc import Callable
from typing_extensions import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import async_session_factory
from app.modules.auth.repository import RefreshTokenRepository, UserRepository
from app.modules.clients.repository import ClientRepository
from app.modules.dashboard.repository import DashboardRepository
from app.modules.executors.repository import ExecutorRepository
from app.modules.materials.repository import MaterialRepository
from app.modules.works.repository import WorkRepository


class SQLAlchemyUnitOfWork:
    def __init__(self, session_factory: Callable[[], AsyncSession] = async_session_factory):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        self.users = UserRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        self.clients = ClientRepository(self.session)
        self.executors = ExecutorRepository(self.session)
        self.materials = MaterialRepository(self.session)
        self.works = WorkRepository(self.session)
        self.dashboard = DashboardRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc:
            await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("UnitOfWork has not been entered.")
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("UnitOfWork has not been entered.")
        await self.session.rollback()
