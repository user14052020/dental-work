from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_doctor_search_document
from app.common.services import SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.doctor import Doctor
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.doctors.schemas import DoctorCreate, DoctorListResponse, DoctorRead, DoctorUpdate


class DoctorService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService):
        self._uow = uow
        self._search = search

    async def list_doctors(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
        client_id: str | None,
    ) -> DoctorListResponse:
        search_ids = await self._search.search_doctors(search) if search else None
        async with self._uow as uow:
            items, total_items = await uow.doctors.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                active_only=active_only,
                client_id=client_id,
                ids=search_ids if search_ids else None,
            )
            rows = [self._map_doctor(item) for item in items]
        return PaginatedResponse[DoctorRead].create(rows, page=page, page_size=page_size, total_items=total_items)

    async def get_doctor(self, doctor_id: str) -> DoctorRead:
        async with self._uow as uow:
            doctor = await uow.doctors.get(doctor_id)
            if doctor is None:
                raise NotFoundError("doctor", doctor_id)
            return self._map_doctor(doctor)

    async def create_doctor(self, payload: DoctorCreate) -> DoctorRead:
        async with self._uow as uow:
            if payload.client_id:
                client = await uow.clients.get(payload.client_id)
                if client is None:
                    raise NotFoundError("client", payload.client_id)
            doctor = await uow.doctors.add(Doctor(**payload.model_dump()))
            await uow.commit()
            doctor = await uow.doctors.get(doctor.id)
        await self._search.index_document(
            settings.elasticsearch_doctors_index,
            doctor.id,
            build_doctor_search_document(doctor),
        )
        return self._map_doctor(doctor)

    async def update_doctor(self, doctor_id: str, payload: DoctorUpdate) -> DoctorRead:
        async with self._uow as uow:
            doctor = await uow.doctors.get(doctor_id)
            if doctor is None:
                raise NotFoundError("doctor", doctor_id)
            data = payload.model_dump(exclude_unset=True)
            if "client_id" in data and data["client_id"]:
                client = await uow.clients.get(data["client_id"])
                if client is None:
                    raise NotFoundError("client", data["client_id"])
            for field, value in data.items():
                setattr(doctor, field, value)
            await uow.commit()
            doctor = await uow.doctors.get(doctor.id)
        await self._search.index_document(
            settings.elasticsearch_doctors_index,
            doctor.id,
            build_doctor_search_document(doctor),
        )
        return self._map_doctor(doctor)

    @staticmethod
    def _map_doctor(doctor: Doctor) -> DoctorRead:
        return DoctorRead(
            id=doctor.id,
            created_at=doctor.created_at,
            updated_at=doctor.updated_at,
            client_id=doctor.client_id,
            client_name=doctor.client.name if doctor.client else None,
            full_name=doctor.full_name,
            phone=doctor.phone,
            email=doctor.email,
            specialization=doctor.specialization,
            comment=doctor.comment,
            is_active=doctor.is_active,
        )
