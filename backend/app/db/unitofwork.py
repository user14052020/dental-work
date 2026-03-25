from __future__ import annotations

from collections.abc import Callable
from typing_extensions import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import async_session_factory
from app.modules.auth.repository import RefreshTokenRepository, UserRepository
from app.modules.clients.repository import ClientRepository
from app.modules.contractors.repository import ContractorRepository
from app.modules.dashboard.repository import DashboardRepository
from app.modules.doctors.repository import DoctorRepository
from app.modules.executors.repository import ExecutorRepository
from app.modules.inventory_adjustments.repository import InventoryAdjustmentRepository
from app.modules.materials.repository import MaterialRepository
from app.modules.narads.repository import NaradRepository
from app.modules.organization.repository import OrganizationRepository
from app.modules.operations.repository import OperationRepository
from app.modules.payments.repository import PaymentRepository
from app.modules.receipts.repository import MaterialReceiptRepository
from app.modules.reports.repository import ReportsRepository
from app.modules.work_catalog.repository import WorkCatalogRepository
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
        self.contractors = ContractorRepository(self.session)
        self.executors = ExecutorRepository(self.session)
        self.inventory_adjustments = InventoryAdjustmentRepository(self.session)
        self.doctors = DoctorRepository(self.session)
        self.materials = MaterialRepository(self.session)
        self.narads = NaradRepository(self.session)
        self.organization = OrganizationRepository(self.session)
        self.operations = OperationRepository(self.session)
        self.payments = PaymentRepository(self.session)
        self.receipts = MaterialReceiptRepository(self.session)
        self.reports = ReportsRepository(self.session)
        self.work_catalog = WorkCatalogRepository(self.session)
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
