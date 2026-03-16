from __future__ import annotations

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.common.services import CacheService, SearchService
from app.core.exceptions import AuthenticationError
from app.core.resources import redis_client, search_client
from app.core.security import decode_access_token
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.auth.schemas import UserRead
from app.modules.auth.service import AuthService
from app.modules.clients.service import ClientService
from app.modules.cost_calculation.service import CostCalculationService
from app.modules.dashboard.service import DashboardService
from app.modules.executors.service import ExecutorService
from app.modules.materials.service import MaterialService
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


def get_executor_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> ExecutorService:
    return ExecutorService(uow=uow, cache=cache, search=search)


def get_material_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
    search: SearchService = Depends(get_search_service),
) -> MaterialService:
    return MaterialService(uow=uow, cache=cache, search=search)


def get_work_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
) -> WorkService:
    return WorkService(uow=uow, search=search, cache=cache)


def get_cost_calculation_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CostCalculationService:
    return CostCalculationService(uow=uow)


def get_dashboard_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> DashboardService:
    return DashboardService(uow=uow, cache=cache)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    if credentials is None:
        raise AuthenticationError("Authorization header is required.")
    payload = decode_access_token(credentials.credentials)
    return await auth_service.get_current_user(payload["sub"])
