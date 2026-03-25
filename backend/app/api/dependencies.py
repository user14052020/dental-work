from __future__ import annotations

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.common.services import CacheService, SearchService
from app.common.permissions import has_permission
from app.core.exceptions import AuthorizationError
from app.core.exceptions import AuthenticationError
from app.core.resources import redis_client, search_client
from app.core.security import decode_access_token
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.auth.schemas import UserRead
from app.modules.auth.service import AuthService
from app.modules.clients.service import ClientService
from app.modules.contractors.service import ContractorService
from app.modules.cost_calculation.service import CostCalculationService
from app.modules.dashboard.service import DashboardService
from app.modules.delivery.service import DeliveryService
from app.modules.doctors.service import DoctorService
from app.modules.executors.service import ExecutorService
from app.modules.inventory_adjustments.service import InventoryAdjustmentService
from app.modules.employees.service import EmployeeService
from app.modules.materials.service import MaterialService
from app.modules.narads.service import NaradService
from app.modules.organization.service import OrganizationService
from app.modules.documents.service import DocumentService
from app.modules.operations.service import OperationService
from app.modules.payments.service import PaymentService
from app.modules.receipts.service import MaterialReceiptService
from app.modules.reports.service import ReportsService
from app.modules.work_catalog.service import WorkCatalogService
from app.modules.works.service import WorkService


bearer_scheme = HTTPBearer(auto_error=False)


def get_uow() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork()


def get_cache_service() -> CacheService:
    return CacheService(redis_client)


def get_search_service() -> SearchService:
    return SearchService(search_client)


def get_auth_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> AuthService:
    return AuthService(uow=uow)


def get_client_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
) -> ClientService:
    return ClientService(uow=uow, search=search, cache=cache)


def get_contractor_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ContractorService:
    return ContractorService(uow=uow)


def get_executor_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> ExecutorService:
    return ExecutorService(uow=uow, cache=cache, search=search)


def get_employee_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> EmployeeService:
    return EmployeeService(uow=uow)


def get_doctor_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
) -> DoctorService:
    return DoctorService(uow=uow, search=search)


def get_material_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> MaterialService:
    return MaterialService(uow=uow, cache=cache, search=search)


def get_inventory_adjustment_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> InventoryAdjustmentService:
    return InventoryAdjustmentService(uow=uow, cache=cache, search=search)


def get_narad_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
) -> NaradService:
    return NaradService(uow=uow, search=search, cache=cache)


def get_operation_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
) -> OperationService:
    return OperationService(uow=uow, search=search)


def get_work_catalog_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
) -> WorkCatalogService:
    return WorkCatalogService(uow=uow, search=search)


def get_organization_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> OrganizationService:
    return OrganizationService(uow=uow)


def get_document_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> DocumentService:
    return DocumentService(uow=uow)


def get_delivery_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
) -> DeliveryService:
    return DeliveryService(uow=uow, search=search, cache=cache)


def get_work_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
) -> WorkService:
    return WorkService(uow=uow, search=search, cache=cache)


def get_payment_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> PaymentService:
    return PaymentService(uow=uow, cache=cache, search=search)


def get_material_receipt_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> MaterialReceiptService:
    return MaterialReceiptService(uow=uow, cache=cache, search=search)


def get_cost_calculation_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CostCalculationService:
    return CostCalculationService(uow=uow)


def get_dashboard_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> DashboardService:
    return DashboardService(uow=uow, cache=cache)


def get_reports_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ReportsService:
    return ReportsService(uow=uow)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    if credentials is None:
        raise AuthenticationError("Authorization header is required.")
    payload = decode_access_token(credentials.credentials)
    return await auth_service.get_current_user(payload["sub"])


def require_permissions(*permission_codes: str):
    async def dependency(current_user: UserRead = Depends(get_current_user)) -> UserRead:
        if permission_codes and not any(has_permission(current_user.permission_codes, code) for code in permission_codes):
            raise AuthorizationError()
        return current_user

    return dependency
