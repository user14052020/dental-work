from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm.attributes import NO_VALUE

from app.db.models.client import Client
from app.db.models.doctor import Doctor
from app.db.models.executor import Executor
from app.db.models.material import Material
from app.db.models.operation import OperationCatalog
from app.db.models.work import Work
from app.db.models.work_catalog import WorkCatalogItem
from app.modules.works.tooth_selection import build_tooth_selection_search_blob


def build_client_search_document(client: Client) -> dict[str, Any]:
    legal_name = getattr(client, "legal_name", None)
    legal_address = getattr(client, "legal_address", None)
    inn = getattr(client, "inn", None)
    kpp = getattr(client, "kpp", None)
    ogrn = getattr(client, "ogrn", None)
    bank_name = getattr(client, "bank_name", None)
    bik = getattr(client, "bik", None)
    settlement_account = getattr(client, "settlement_account", None)
    correspondent_account = getattr(client, "correspondent_account", None)
    contract_number = getattr(client, "contract_number", None)
    contract_date = getattr(client, "contract_date", None)
    signer_name = getattr(client, "signer_name", None)
    catalog_prices = _get_loaded_relation(client, "catalog_prices", [])
    catalog_price_codes = [
        resolved_item.code
        for price in catalog_prices
        if (resolved_item := _get_loaded_relation(price, "catalog_item")) and resolved_item.code
    ]
    catalog_price_names = [
        resolved_item.name
        for price in catalog_prices
        if (resolved_item := _get_loaded_relation(price, "catalog_item")) and resolved_item.name
    ]
    catalog_price_values = [_serialize_search_value(getattr(price, "price", None)) for price in catalog_prices]
    catalog_price_comments = [getattr(price, "comment", None) for price in catalog_prices]

    return {
        "name": client.name,
        "contact_person": getattr(client, "contact_person", None),
        "email": getattr(client, "email", None),
        "phone": getattr(client, "phone", None),
        "address": getattr(client, "address", None),
        "delivery_address": getattr(client, "delivery_address", None),
        "delivery_contact": getattr(client, "delivery_contact", None),
        "delivery_phone": getattr(client, "delivery_phone", None),
        "legal_name": legal_name,
        "legal_address": legal_address,
        "inn": inn,
        "kpp": kpp,
        "ogrn": ogrn,
        "bank_name": bank_name,
        "bik": bik,
        "settlement_account": settlement_account,
        "correspondent_account": correspondent_account,
        "contract_number": contract_number,
        "contract_date": _serialize_search_value(contract_date),
        "signer_name": signer_name,
        "default_price_adjustment_percent": _serialize_search_value(
            getattr(client, "default_price_adjustment_percent", None)
        ),
        "catalog_price_codes": catalog_price_codes,
        "catalog_price_names": catalog_price_names,
        "catalog_price_values": catalog_price_values,
        "catalog_price_comments": catalog_price_comments,
        "comment": getattr(client, "comment", None),
        "search_blob": build_search_blob(
            [
                client.name,
                getattr(client, "contact_person", None),
                getattr(client, "email", None),
                getattr(client, "phone", None),
                getattr(client, "address", None),
                getattr(client, "delivery_address", None),
                getattr(client, "delivery_contact", None),
                getattr(client, "delivery_phone", None),
                legal_name,
                legal_address,
                inn,
                kpp,
                ogrn,
                bank_name,
                bik,
                settlement_account,
                correspondent_account,
                contract_number,
                contract_date,
                signer_name,
                getattr(client, "default_price_adjustment_percent", None),
                *catalog_price_codes,
                *catalog_price_names,
                *catalog_price_values,
                *catalog_price_comments,
                getattr(client, "comment", None),
            ]
        ),
    }


def build_executor_search_document(executor: Executor) -> dict[str, Any]:
    payment_category = _get_loaded_relation(executor, "payment_category")
    payment_category_name = payment_category.name if payment_category else None
    payment_category_code = payment_category.code if payment_category else None
    return {
        "full_name": executor.full_name,
        "phone": executor.phone,
        "email": executor.email,
        "specialization": executor.specialization,
        "payment_category_name": payment_category_name,
        "payment_category_code": payment_category_code,
        "hourly_rate": _serialize_search_value(executor.hourly_rate),
        "comment": executor.comment,
        "is_active": _serialize_search_value(executor.is_active),
        "search_blob": build_search_blob(
            [
                executor.full_name,
                executor.phone,
                executor.email,
                executor.specialization,
                payment_category_name,
                payment_category_code,
                executor.hourly_rate,
                executor.comment,
                executor.is_active,
            ]
        ),
    }


def build_doctor_search_document(doctor: Doctor) -> dict[str, Any]:
    resolved_client = _get_loaded_relation(doctor, "client")
    client_name = resolved_client.name if resolved_client else None
    return {
        "full_name": doctor.full_name,
        "client_name": client_name,
        "client_id": doctor.client_id,
        "phone": doctor.phone,
        "email": doctor.email,
        "specialization": doctor.specialization,
        "comment": doctor.comment,
        "is_active": _serialize_search_value(doctor.is_active),
        "search_blob": build_search_blob(
            [
                doctor.full_name,
                client_name,
                doctor.client_id,
                doctor.phone,
                doctor.email,
                doctor.specialization,
                doctor.comment,
                doctor.is_active,
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


def build_work_catalog_search_document(item: WorkCatalogItem) -> dict[str, Any]:
    default_operations = _get_loaded_relation(item, "default_operations", [])
    operation_names = [
        resolved_operation.name
        for operation in default_operations
        if (resolved_operation := _get_loaded_relation(operation, "operation")) and resolved_operation.name
    ]
    operation_codes = [
        resolved_operation.code
        for operation in default_operations
        if (resolved_operation := _get_loaded_relation(operation, "operation")) and resolved_operation.code
    ]
    return {
        "code": item.code,
        "name": item.name,
        "category": item.category,
        "description": item.description,
        "base_price": _serialize_search_value(item.base_price),
        "default_duration_hours": _serialize_search_value(item.default_duration_hours),
        "is_active": _serialize_search_value(item.is_active),
        "operation_names": operation_names,
        "operation_codes": operation_codes,
        "search_blob": build_search_blob(
            [
                item.code,
                item.name,
                item.category,
                item.description,
                item.base_price,
                item.default_duration_hours,
                item.is_active,
                *operation_names,
                *operation_codes,
            ]
        ),
    }


def build_work_search_document(
    work: Work,
    *,
    client_name: Optional[str] = None,
    executor_name: Optional[str] = None,
    doctor_name: Optional[str] = None,
    work_catalog_item_name: Optional[str] = None,
    work_catalog_item_code: Optional[str] = None,
    work_catalog_item_category: Optional[str] = None,
    work_item_types: Optional[list[str]] = None,
    work_item_codes: Optional[list[str]] = None,
    work_item_descriptions: Optional[list[str]] = None,
    operation_names: Optional[list[str]] = None,
    material_names: Optional[list[str]] = None,
    attachment_names: Optional[list[str]] = None,
) -> dict[str, Any]:
    resolved_client = None if client_name is not None else _get_loaded_relation(work, "client")
    resolved_executor = None if executor_name is not None else _get_loaded_relation(work, "executor")
    resolved_doctor = None if doctor_name is not None else _get_loaded_relation(work, "doctor")
    resolved_catalog_item = (
        None
        if work_catalog_item_name is not None
        or work_catalog_item_code is not None
        or work_catalog_item_category is not None
        else _get_loaded_relation(work, "catalog_item")
    )
    resolved_materials = [] if material_names is not None else _get_loaded_relation(work, "materials", [])
    resolved_operations = [] if operation_names is not None else _get_loaded_relation(work, "work_operations", [])
    resolved_attachments = [] if attachment_names is not None else _get_loaded_relation(work, "attachments", [])
    resolved_work_items = (
        []
        if work_item_types is not None or work_item_codes is not None or work_item_descriptions is not None
        else _get_loaded_relation(work, "work_items", [])
    )

    resolved_client_name = (
        client_name if client_name is not None else (resolved_client.name if resolved_client else None)
    )
    resolved_client_delivery_address = getattr(resolved_client, "delivery_address", None) if resolved_client else None
    resolved_client_delivery_contact = getattr(resolved_client, "delivery_contact", None) if resolved_client else None
    resolved_client_delivery_phone = getattr(resolved_client, "delivery_phone", None) if resolved_client else None
    resolved_executor_name = (
        executor_name if executor_name is not None else (resolved_executor.full_name if resolved_executor else None)
    )
    resolved_doctor_name = doctor_name if doctor_name is not None else (resolved_doctor.full_name if resolved_doctor else None)
    resolved_catalog_item_name = (
        work_catalog_item_name
        if work_catalog_item_name is not None
        else (resolved_catalog_item.name if resolved_catalog_item else None)
    )
    resolved_catalog_item_code = (
        work_catalog_item_code
        if work_catalog_item_code is not None
        else (resolved_catalog_item.code if resolved_catalog_item else None)
    )
    resolved_catalog_item_category = (
        work_catalog_item_category
        if work_catalog_item_category is not None
        else (resolved_catalog_item.category if resolved_catalog_item else None)
    )
    resolved_material_names = (
        material_names
        if material_names is not None
        else [
            material.name
            for item in resolved_materials
            if (material := _get_loaded_relation(item, "material")) and material.name
        ]
    )
    resolved_operation_names = (
        operation_names
        if operation_names is not None
        else [item.operation_name for item in resolved_operations if item.operation_name]
    )
    resolved_work_item_types = (
        work_item_types
        if work_item_types is not None
        else [item.work_type for item in resolved_work_items if getattr(item, "work_type", None)]
    )
    resolved_work_item_codes = (
        work_item_codes
        if work_item_codes is not None
        else [
            catalog_item.code
            for item in resolved_work_items
            if (catalog_item := _get_loaded_relation(item, "catalog_item")) and catalog_item.code
        ]
    )
    resolved_work_item_descriptions = (
        work_item_descriptions
        if work_item_descriptions is not None
        else [item.description for item in resolved_work_items if getattr(item, "description", None)]
    )
    resolved_attachment_names = (
        attachment_names
        if attachment_names is not None
        else [item.file_name for item in resolved_attachments if getattr(item, "file_name", None)]
    )

    return {
        "order_number": work.order_number,
        "client_name": resolved_client_name,
        "client_delivery_address": resolved_client_delivery_address,
        "client_delivery_contact": resolved_client_delivery_contact,
        "client_delivery_phone": resolved_client_delivery_phone,
        "client_id": work.client_id,
        "executor_name": resolved_executor_name,
        "executor_id": work.executor_id,
        "doctor_id": getattr(work, "doctor_id", None),
        "doctor_name": resolved_doctor_name or work.doctor_name,
        "work_catalog_item_id": getattr(work, "work_catalog_item_id", None),
        "work_catalog_item_code": resolved_catalog_item_code,
        "work_catalog_item_name": resolved_catalog_item_name,
        "work_catalog_item_category": resolved_catalog_item_category,
        "work_type": work.work_type,
        "description": work.description,
        "doctor_phone": getattr(work, "doctor_phone", None),
        "patient_name": work.patient_name,
        "patient_age": _serialize_search_value(getattr(work, "patient_age", None)),
        "patient_gender": getattr(work, "patient_gender", None),
        "require_color_photo": _serialize_search_value(getattr(work, "require_color_photo", None)),
        "face_shape": getattr(work, "face_shape", None),
        "implant_system": getattr(work, "implant_system", None),
        "metal_type": getattr(work, "metal_type", None),
        "shade_color": getattr(work, "shade_color", None),
        "tooth_formula": getattr(work, "tooth_formula", None),
        "status": work.status,
        "received_at": _serialize_search_value(work.received_at),
        "deadline_at": _serialize_search_value(work.deadline_at),
        "completed_at": _serialize_search_value(work.completed_at),
        "closed_at": _serialize_search_value(work.closed_at),
        "delivery_sent": _serialize_search_value(getattr(work, "delivery_sent", None)),
        "delivery_sent_at": _serialize_search_value(getattr(work, "delivery_sent_at", None)),
        "base_price_for_client": _serialize_search_value(getattr(work, "base_price_for_client", None)),
        "price_adjustment_percent": _serialize_search_value(getattr(work, "price_adjustment_percent", None)),
        "price_for_client": _serialize_search_value(getattr(work, "price_for_client", None)),
        "cost_price": _serialize_search_value(getattr(work, "cost_price", None)),
        "margin": _serialize_search_value(getattr(work, "margin", None)),
        "additional_expenses": _serialize_search_value(getattr(work, "additional_expenses", None)),
        "labor_hours": _serialize_search_value(getattr(work, "labor_hours", None)),
        "labor_cost": _serialize_search_value(getattr(work, "labor_cost", None)),
        "amount_paid": _serialize_search_value(getattr(work, "amount_paid", None)),
        "tooth_selection_summary": build_tooth_selection_search_blob(getattr(work, "tooth_selection", None) or []),
        "work_item_types": resolved_work_item_types,
        "work_item_codes": resolved_work_item_codes,
        "work_item_descriptions": resolved_work_item_descriptions,
        "operation_names": resolved_operation_names,
        "material_names": resolved_material_names,
        "attachment_names": resolved_attachment_names,
        "search_blob": build_search_blob(
            [
                work.order_number,
                resolved_client_name,
                resolved_client_delivery_address,
                resolved_client_delivery_contact,
                resolved_client_delivery_phone,
                work.client_id,
                resolved_executor_name,
                work.executor_id,
                getattr(work, "doctor_id", None),
                resolved_doctor_name or work.doctor_name,
                getattr(work, "work_catalog_item_id", None),
                resolved_catalog_item_code,
                resolved_catalog_item_name,
                resolved_catalog_item_category,
                work.work_type,
                work.description,
                getattr(work, "doctor_phone", None),
                work.patient_name,
                getattr(work, "patient_age", None),
                getattr(work, "patient_gender", None),
                getattr(work, "require_color_photo", None),
                getattr(work, "face_shape", None),
                getattr(work, "implant_system", None),
                getattr(work, "metal_type", None),
                getattr(work, "shade_color", None),
                getattr(work, "tooth_formula", None),
                work.status,
                work.received_at,
                work.deadline_at,
                work.completed_at,
                work.closed_at,
                getattr(work, "delivery_sent", None),
                getattr(work, "delivery_sent_at", None),
                getattr(work, "base_price_for_client", None),
                getattr(work, "price_adjustment_percent", None),
                getattr(work, "price_for_client", None),
                getattr(work, "cost_price", None),
                getattr(work, "margin", None),
                getattr(work, "additional_expenses", None),
                getattr(work, "labor_hours", None),
                getattr(work, "labor_cost", None),
                getattr(work, "amount_paid", None),
                build_tooth_selection_search_blob(getattr(work, "tooth_selection", None) or []),
                *resolved_work_item_types,
                *resolved_work_item_codes,
                *resolved_work_item_descriptions,
                *resolved_operation_names,
                *resolved_material_names,
                *resolved_attachment_names,
            ]
        ),
    }


def build_operation_search_document(operation: OperationCatalog) -> dict[str, Any]:
    rate_tokens = [
        f"{rate.executor_category.code} {rate.executor_category.name} {_serialize_search_value(rate.labor_rate) or ''}".strip()
        for rate in operation.payment_rates
        if rate.executor_category
    ]
    return {
        "code": operation.code,
        "name": operation.name,
        "operation_group": operation.operation_group,
        "description": operation.description,
        "default_quantity": _serialize_search_value(operation.default_quantity),
        "default_duration_hours": _serialize_search_value(operation.default_duration_hours),
        "is_active": _serialize_search_value(operation.is_active),
        "rates_summary": rate_tokens,
        "search_blob": build_search_blob(
            [
                operation.code,
                operation.name,
                operation.operation_group,
                operation.description,
                operation.default_quantity,
                operation.default_duration_hours,
                operation.is_active,
                *rate_tokens,
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


def _get_loaded_relation(instance: Any, attr_name: str, default: Any = None) -> Any:
    try:
        state = inspect(instance)
    except NoInspectionAvailable:
        instance_dict = getattr(instance, "__dict__", {})
        if attr_name in instance_dict:
            return instance_dict[attr_name]
        return default

    try:
        loaded_value = state.attrs[attr_name].loaded_value
    except (AttributeError, KeyError):
        instance_dict = getattr(instance, "__dict__", {})
        if attr_name in instance_dict:
            return instance_dict[attr_name]
        return default

    if loaded_value is NO_VALUE:
        return default

    return loaded_value
