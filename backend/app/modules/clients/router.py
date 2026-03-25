from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_client_service, get_current_user, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.clients.schemas import ClientCreate, ClientDetailRead, ClientListResponse, ClientRead, ClientUpdate
from app.modules.clients.service import ClientService


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("clients.manage"))],
)


@router.get("", response_model=ClientListResponse)
async def list_clients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=255),
    service: ClientService = Depends(get_client_service),
) -> ClientListResponse:
    return await service.list_clients(page=page, page_size=page_size, search=search)


@router.get("/{client_id}", response_model=ClientDetailRead)
async def get_client(client_id: str, service: ClientService = Depends(get_client_service)) -> ClientDetailRead:
    return await service.get_client(client_id)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    service: ClientService = Depends(get_client_service),
) -> ClientRead:
    return await service.create_client(payload)


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    service: ClientService = Depends(get_client_service),
) -> ClientRead:
    return await service.update_client(client_id, payload)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: str, service: ClientService = Depends(get_client_service)) -> Response:
    await service.delete_client(client_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
