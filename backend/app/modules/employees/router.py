from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_employee_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.employees.schemas import EmployeeCreate, EmployeeListResponse, EmployeeRead, EmployeeUpdate
from app.modules.employees.service import EmployeeService


router = APIRouter(prefix="/employees", tags=["employees"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    include_fired: bool = Query(default=False),
    _: UserRead = Depends(require_permissions("employees.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeListResponse:
    return await service.list_employees(
        page=page,
        page_size=page_size,
        search=search,
        include_fired=include_fired,
    )


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(
    employee_id: str,
    _: UserRead = Depends(require_permissions("employees.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.get_employee(employee_id)


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    current_user: UserRead = Depends(require_permissions("employees.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.create_employee(payload, current_user=current_user)


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    current_user: UserRead = Depends(require_permissions("employees.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.update_employee(employee_id, payload, current_user=current_user)
