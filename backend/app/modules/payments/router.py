from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_current_user, get_payment_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.payments.schemas import (
    NaradPaymentCandidateRead,
    PaymentCreate,
    PaymentListResponse,
    PaymentRead,
    PaymentReturnNaradAllocation,
    PaymentUpdate,
    WorkPaymentCandidateRead,
)
from app.modules.payments.service import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("payments.manage"))],
)


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    client_id: Optional[str] = Query(default=None),
    method: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    return await service.list_payments(
        page=page,
        page_size=page_size,
        search=search,
        client_id=client_id,
        method=method,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/work-candidates", response_model=list[WorkPaymentCandidateRead])
async def list_payment_work_candidates(
    client_id: str = Query(...),
    payment_id: Optional[str] = Query(default=None),
    service: PaymentService = Depends(get_payment_service),
) -> list[WorkPaymentCandidateRead]:
    return await service.list_work_candidates(client_id, payment_id=payment_id)


@router.get("/narad-candidates", response_model=list[NaradPaymentCandidateRead])
async def list_payment_narad_candidates(
    client_id: str = Query(...),
    payment_id: Optional[str] = Query(default=None),
    service: PaymentService = Depends(get_payment_service),
) -> list[NaradPaymentCandidateRead]:
    return await service.list_narad_candidates(client_id, payment_id=payment_id)


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(payment_id: str, service: PaymentService = Depends(get_payment_service)) -> PaymentRead:
    return await service.get_payment(payment_id)


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    current_user: UserRead = Depends(require_permissions("payments.manage")),
) -> PaymentRead:
    return await service.create_payment(payload, actor_email=current_user.email)


@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: str,
    payload: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
    current_user: UserRead = Depends(require_permissions("payments.manage")),
) -> PaymentRead:
    return await service.update_payment(payment_id, payload, actor_email=current_user.email)


@router.post("/{payment_id}/return-narad-allocation", response_model=PaymentRead)
async def return_narad_allocation(
    payment_id: str,
    payload: PaymentReturnNaradAllocation,
    service: PaymentService = Depends(get_payment_service),
    current_user: UserRead = Depends(require_permissions("payments.manage")),
) -> PaymentRead:
    return await service.return_narad_allocation(payment_id, payload, actor_email=current_user.email)


@router.post("/{payment_id}/delete-unallocated-balance", response_model=PaymentRead)
async def delete_unallocated_balance(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
    current_user: UserRead = Depends(require_permissions("payments.manage")),
) -> PaymentRead:
    return await service.delete_unallocated_balance(payment_id, actor_email=current_user.email)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
    current_user: UserRead = Depends(require_permissions("payments.manage")),
) -> Response:
    await service.delete_payment(payment_id, actor_email=current_user.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
