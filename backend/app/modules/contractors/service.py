from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.core.exceptions import NotFoundError
from app.db.models.contractor import Contractor
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.contractors.schemas import (
    ContractorCreate,
    ContractorListResponse,
    ContractorRead,
    ContractorUpdate,
)


class ContractorService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def list_contractors(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
    ) -> ContractorListResponse:
        async with self._uow as uow:
            items, total_items = await uow.contractors.list(
                page=page,
                page_size=page_size,
                search=search,
                active_only=active_only,
            )
            rows = [self._map_contractor(item) for item in items]
        return PaginatedResponse[ContractorRead].create(rows, page=page, page_size=page_size, total_items=total_items)

    async def get_contractor(self, contractor_id: str) -> ContractorRead:
        async with self._uow as uow:
            contractor = await uow.contractors.get(contractor_id)
            if contractor is None:
                raise NotFoundError("contractor", contractor_id)
            return self._map_contractor(contractor)

    async def create_contractor(self, payload: ContractorCreate) -> ContractorRead:
        async with self._uow as uow:
            contractor = await uow.contractors.add(Contractor(**payload.model_dump()))
            await uow.commit()
            contractor = await uow.contractors.get(contractor.id)
        return self._map_contractor(contractor)

    async def update_contractor(self, contractor_id: str, payload: ContractorUpdate) -> ContractorRead:
        async with self._uow as uow:
            contractor = await uow.contractors.get(contractor_id)
            if contractor is None:
                raise NotFoundError("contractor", contractor_id)
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(contractor, field, value)
            await uow.commit()
            contractor = await uow.contractors.get(contractor.id)
        return self._map_contractor(contractor)

    @staticmethod
    def _map_contractor(contractor: Contractor) -> ContractorRead:
        return ContractorRead(
            id=contractor.id,
            created_at=contractor.created_at,
            updated_at=contractor.updated_at,
            name=contractor.name,
            contact_person=contractor.contact_person,
            phone=contractor.phone,
            email=contractor.email,
            address=contractor.address,
            comment=contractor.comment,
            is_active=contractor.is_active,
        )
