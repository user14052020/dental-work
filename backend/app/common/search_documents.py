from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional

from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.material import Material
from app.db.models.work import Work


def build_client_search_document(client: Client) -> dict[str, Any]:
    return {
        "name": client.name,
        "contact_person": client.contact_person,
        "email": client.email,
        "phone": client.phone,
        "address": client.address,
        "comment": client.comment,
        "search_blob": build_search_blob(
            [client.name, client.contact_person, client.email, client.phone, client.address, client.comment]
        ),
    }


def build_executor_search_document(executor: Executor) -> dict[str, Any]:
    return {
        "full_name": executor.full_name,
        "phone": executor.phone,
        "email": executor.email,
        "specialization": executor.specialization,
        "hourly_rate": _serialize_search_value(executor.hourly_rate),
        "comment": executor.comment,
        "is_active": _serialize_search_value(executor.is_active),
        "search_blob": build_search_blob(
            [
                executor.full_name,
                executor.phone,
                executor.email,
                executor.specialization,
                executor.hourly_rate,
                executor.comment,
                executor.is_active,
            ]
        ),
    }


def build_material_search_document(material: Material) -> dict[str, Any]:
    return {
        "name": material.name,
        "category": material.category,
        "unit": material.unit,
        "stock": _serialize_search_value(material.stock),
        "purchase_price": _serialize_search_value(material.purchase_price),
        "average_price": _serialize_search_value(material.average_price),
        "supplier": material.supplier,
        "min_stock": _serialize_search_value(material.min_stock),
        "comment": material.comment,
        "search_blob": build_search_blob(
            [
                material.name,
                material.category,
                material.unit,
                material.stock,
                material.purchase_price,
                material.average_price,
                material.supplier,
                material.min_stock,
                material.comment,
            ]
        ),
    }


def build_work_search_document(
    work: Work,
    *,
    client_name: Optional[str] = None,
    executor_name: Optional[str] = None,
    material_names: Optional[list[str]] = None,
) -> dict[str, Any]:
    resolved_client_name = client_name or (work.client.name if getattr(work, "client", None) else None)
    resolved_executor_name = executor_name or (
        work.executor.full_name if getattr(work, "executor", None) else None
    )
    resolved_material_names = material_names or [
        item.material.name
        for item in getattr(work, "materials", [])
        if getattr(item, "material", None) and item.material.name
    ]

    return {
        "order_number": work.order_number,
        "client_name": resolved_client_name,
        "client_id": work.client_id,
        "executor_name": resolved_executor_name,
        "executor_id": work.executor_id,
        "work_type": work.work_type,
        "description": work.description,
        "status": work.status,
        "received_at": _serialize_search_value(work.received_at),
        "deadline_at": _serialize_search_value(work.deadline_at),
        "completed_at": _serialize_search_value(work.completed_at),
        "price_for_client": _serialize_search_value(work.price_for_client),
        "cost_price": _serialize_search_value(work.cost_price),
        "margin": _serialize_search_value(work.margin),
        "additional_expenses": _serialize_search_value(work.additional_expenses),
        "labor_hours": _serialize_search_value(work.labor_hours),
        "amount_paid": _serialize_search_value(work.amount_paid),
        "comment": work.comment,
        "material_names": resolved_material_names,
        "search_blob": build_search_blob(
            [
                work.order_number,
                resolved_client_name,
                work.client_id,
                resolved_executor_name,
                work.executor_id,
                work.work_type,
                work.description,
                work.status,
                work.received_at,
                work.deadline_at,
                work.completed_at,
                work.price_for_client,
                work.cost_price,
                work.margin,
                work.additional_expenses,
                work.labor_hours,
                work.amount_paid,
                work.comment,
                *resolved_material_names,
            ]
        ),
    }


def build_search_blob(values: Iterable[object | None]) -> str:
    return " ".join(filter(None, (_serialize_search_value(value) for value in values)))


def _serialize_search_value(value: object | None) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    text = str(value).strip()
    return text or None
