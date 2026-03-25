from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_doctor_service, require_permissions
from app.modules.doctors.schemas import DoctorCreate, DoctorListResponse, DoctorRead, DoctorUpdate
from app.modules.doctors.service import DoctorService


router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("doctors.manage"))],
)


@router.get("", response_model=DoctorListResponse)
async def list_doctors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    client_id: Optional[str] = Query(default=None),
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorListResponse:
    return await service.list_doctors(
        page=page,
        page_size=page_size,
        search=search,
        active_only=active_only,
        client_id=client_id,
    )


@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(
    doctor_id: str,
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorRead:
    return await service.get_doctor(doctor_id)


@router.post("", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    payload: DoctorCreate,
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorRead:
    return await service.create_doctor(payload)


@router.patch("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(
    doctor_id: str,
    payload: DoctorUpdate,
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorRead:
    return await service.update_doctor(doctor_id, payload)
