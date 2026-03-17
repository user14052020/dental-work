from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_organization_service
from app.modules.organization.schemas import OrganizationProfileRead, OrganizationProfileUpsert
from app.modules.organization.service import OrganizationService


router = APIRouter(
    prefix="/organization",
    tags=["organization"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=OrganizationProfileRead)
async def get_organization_profile(
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationProfileRead:
    return await service.get_profile()


@router.put("", response_model=OrganizationProfileRead)
async def upsert_organization_profile(
    payload: OrganizationProfileUpsert,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationProfileRead:
    return await service.upsert_profile(payload)
