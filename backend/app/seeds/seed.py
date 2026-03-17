from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import set_committed_value

from app.common.enums import MaterialUnit, WorkStatus
from app.common.search_documents import (
    build_client_search_document,
    build_doctor_search_document,
    build_executor_search_document,
    build_material_search_document,
    build_operation_search_document,
    build_work_catalog_search_document,
    build_work_search_document,
)
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.resources import redis_client, search_client
from app.core.security import create_access_token, hash_password
from app.db.engine import engine
from app.db.models.client import Client
from app.db.models.client_work_catalog_price import ClientWorkCatalogPrice
from app.db.models.doctor import Doctor
from app.db.models.executor import Executor
from app.db.models.material import Material
from app.db.models.operation import ExecutorCategory, OperationCatalog, OperationCategoryRate, WorkOperation, WorkOperationLog
from app.db.models.organization import OrganizationProfile
from app.db.models.user import User
from app.db.models.work import Work, WorkChangeLog, WorkItem, WorkMaterial
from app.db.models.work_catalog import WorkCatalogItem, WorkCatalogItemOperation
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.works.tooth_selection import build_tooth_formula_from_selection


DEMO_ADMIN_EMAIL = "admin@dentallab.app"
DEMO_ADMIN_PASSWORD = "admin123"
DEMO_WORK_ORDER_NUMBER = "DL-2026-0001"

DEMO_CLIENT_DATA = {
    "name": "Клиника Улыбка",
    "legal_name": "ООО «Клиника Улыбка»",
    "contact_person": "Анна Петрова",
    "phone": "+79991234567",
    "email": "anna@ulybka-clinic.ru",
    "address": "Москва, ул. Тверская, 1",
    "delivery_address": "620026, Екатеринбург, ул. Белинского, 86, вход со двора",
    "delivery_contact": "Администратор Марина Алексеева",
    "delivery_phone": "+79991230001",
    "legal_address": "620014, Екатеринбург, ул. Вайнера, 10",
    "inn": "6671456789",
    "kpp": "667101001",
    "ogrn": "1146671000001",
    "bank_name": "АО МедТех Банк",
    "bik": "044525321",
    "settlement_account": "40702810000000001025",
    "correspondent_account": "30101810400000000321",
    "contract_number": "13025",
    "contract_date": datetime(2026, 2, 6, tzinfo=timezone.utc).date(),
    "signer_name": "Кравцова Л.Ю.",
    "default_price_adjustment_percent": Decimal("-7.50"),
    "comment": "Приоритетный клиент лаборатории",
}

DEMO_ORGANIZATION_DATA = {
    "display_name": "Зуботехническая лаборатория Северный Мост",
    "legal_name": "ООО СЕВЕРНЫЙ МОСТ",
    "short_name": "ООО Северный Мост",
    "legal_address": "620075, Свердловская обл., г. Екатеринбург, ул. Луначарского, д. 80, офис 12",
    "mailing_address": "620075, Свердловская обл., г. Екатеринбург, ул. Луначарского, д. 80, офис 12",
    "phone": "+79995554433",
    "email": "office@severny-most-lab.ru",
    "inn": "6678123456",
    "kpp": "667801001",
    "ogrn": "1246600004321",
    "bank_name": "АО Банк Развитие",
    "bik": "044525987",
    "settlement_account": "40702810400000004321",
    "correspondent_account": "30101810400000000987",
    "recipient_name": "ООО СЕВЕРНЫЙ МОСТ",
    "director_name": "Петрова Н.А.",
    "accountant_name": "Смирнов К.К.",
    "vat_mode": "without_vat",
    "vat_label": "Без налога (НДС)",
    "comment": "Основная организация для печатных форм",
}

DEMO_EXECUTOR_FIXTURES = [
    {
        "full_name": "Дмитрий Иванов",
        "phone": "+79990001122",
        "email": "d.ivanov@dentallab.app",
        "specialization": "Керамика",
        "hourly_rate": Decimal("2800.00"),
        "comment": "Старший техник по керамике",
        "is_active": True,
        "payment_category": {
            "code": "ceramist_a",
            "name": "Керамист A",
            "description": "Базовая категория для керамических работ",
            "sort_order": 10,
            "is_active": True,
        },
    },
    {
        "full_name": "Екатерина Смирнова",
        "phone": "+79990001123",
        "email": "e.smirnova@dentallab.app",
        "specialization": "CAD/CAM и каркасы",
        "hourly_rate": Decimal("2500.00"),
        "comment": "Проектирование и фрезеровка каркасов",
        "is_active": True,
        "payment_category": {
            "code": "cadcam_a",
            "name": "CAD/CAM A",
            "description": "Категория для цифрового моделирования и каркасов",
            "sort_order": 20,
            "is_active": True,
        },
    },
    {
        "full_name": "Артем Кузнецов",
        "phone": "+79990001124",
        "email": "a.kuznetsov@dentallab.app",
        "specialization": "Съемное протезирование",
        "hourly_rate": Decimal("2300.00"),
        "comment": "Полные и частичные съемные конструкции",
        "is_active": True,
        "payment_category": {
            "code": "removable_a",
            "name": "Съемное A",
            "description": "Категория для съемных протезов",
            "sort_order": 30,
            "is_active": True,
        },
    },
    {
        "full_name": "Мария Орлова",
        "phone": "+79990001125",
        "email": "m.orlova@dentallab.app",
        "specialization": "Металл и литье",
        "hourly_rate": Decimal("2400.00"),
        "comment": "Литье и металлические каркасы",
        "is_active": True,
        "payment_category": {
            "code": "metal_a",
            "name": "Металл A",
            "description": "Категория для литейных и металлических работ",
            "sort_order": 40,
            "is_active": True,
        },
    },
    {
        "full_name": "Ольга Миронова",
        "phone": "+79990001126",
        "email": "o.mironova@dentallab.app",
        "specialization": "Финиш и контроль качества",
        "hourly_rate": Decimal("2100.00"),
        "comment": "Финишная обработка и проверка перед выдачей",
        "is_active": True,
        "payment_category": {
            "code": "finish_a",
            "name": "Финиш A",
            "description": "Категория для финальной обработки и контроля",
            "sort_order": 50,
            "is_active": True,
        },
    },
]

DEMO_EXECUTOR_DATA = DEMO_EXECUTOR_FIXTURES[0]
DEMO_EXECUTOR_CATEGORY_DATA = DEMO_EXECUTOR_DATA["payment_category"]

DEMO_DOCTOR_FIXTURES = [
    {
        "full_name": "Сергей Волков",
        "phone": "+79991112233",
        "email": "s.volkov@ulybka-clinic.ru",
        "specialization": "Ортопед",
        "comment": "Основной врач по ортопедическим работам",
        "is_active": True,
    },
    {
        "full_name": "Наталья Егорова",
        "phone": "+79991112234",
        "email": "n.egorova@ulybka-clinic.ru",
        "specialization": "Терапевт",
        "comment": "Врач-контакт по срочным случаям",
        "is_active": True,
    },
    {
        "full_name": "Павел Климов",
        "phone": "+79991112235",
        "email": "p.klimov@ulybka-clinic.ru",
        "specialization": "Имплантолог",
        "comment": "Работы на имплантах и сложные кейсы",
        "is_active": True,
    },
]

DEMO_WORK_CATALOG_FIXTURES = [
    {
        "code": "ZR_CROWN",
        "name": "Циркониевая коронка",
        "category": "Ортопедия",
        "description": "Стандартная циркониевая коронка с облицовкой",
        "base_price": Decimal("16756.76"),
        "default_duration_hours": Decimal("3.50"),
        "is_active": True,
        "sort_order": 10,
        "default_operations": [
            {
                "operation_code": "CROWN_ZR",
                "quantity": Decimal("2.00"),
                "note": "Каркас и облицовка",
                "sort_order": 0,
            }
        ],
    },
    {
        "code": "TEMP_CROWN",
        "name": "Временная коронка",
        "category": "Временные конструкции",
        "description": "Временная ортопедическая конструкция",
        "base_price": Decimal("4200.00"),
        "default_duration_hours": Decimal("1.50"),
        "is_active": True,
        "sort_order": 20,
        "default_operations": [
            {
                "operation_code": "CROWN_ZR",
                "quantity": Decimal("1.00"),
                "note": "Сокращенный производственный цикл",
                "sort_order": 0,
            }
        ],
    },
    {
        "code": "IMPLANT_BRIDGE",
        "name": "Мост на имплантах",
        "category": "Имплантация",
        "description": "Ортопедическая конструкция на имплантах",
        "base_price": Decimal("38900.00"),
        "default_duration_hours": Decimal("5.50"),
        "is_active": True,
        "sort_order": 30,
        "default_operations": [
            {
                "operation_code": "CROWN_ZR",
                "quantity": Decimal("3.00"),
                "note": "Каркас, примерка и финиш",
                "sort_order": 0,
            }
        ],
    },
]

DEMO_CLIENT_CATALOG_PRICES = [
    {
        "code": "ZR_CROWN",
        "price": Decimal("14200.00"),
        "comment": "Специальная цена для постоянного клиента",
    }
]

DEMO_MATERIAL_DATA = {
    "name": "Циркониевый диск",
    "category": "Керамика",
    "unit": MaterialUnit.PIECE.value,
    "stock": Decimal("24.000"),
    "purchase_price": Decimal("5200.00"),
    "average_price": Decimal("5450.00"),
    "supplier": "Дент Снаб",
    "min_stock": Decimal("5.000"),
    "comment": "Многослойный цирконий для коронок",
}

DEMO_OPERATION_DATA = {
    "code": "CROWN_ZR",
    "name": "Циркониевая коронка",
    "operation_group": "Ортопедия",
    "description": "Каркас и облицовка циркониевой коронки",
    "default_quantity": Decimal("1.00"),
    "default_duration_hours": Decimal("1.75"),
    "labor_rate": Decimal("4900.00"),
    "quantity": Decimal("2.00"),
    "note": "Каркас и облицовка",
}

DEMO_WORK_DATA = {
    "order_number": DEMO_WORK_ORDER_NUMBER,
    "work_type": "Циркониевая коронка",
    "description": "Восстановление верхнего моляра",
    "status": WorkStatus.COMPLETED.value,
    "doctor_name": "Сергей Волков",
    "doctor_phone": "+79991112233",
    "patient_name": "Ирина Соколова",
    "patient_age": 34,
    "patient_gender": "female",
    "require_color_photo": True,
    "face_shape": "oval",
    "implant_system": "Straumann",
    "metal_type": "Цирконий",
    "shade_color": "A2",
    "tooth_selection": [
        {"tooth_code": "16", "state": "target", "surfaces": ["occlusal", "mesial"]},
        {"tooth_code": "17", "state": "missing", "surfaces": []},
    ],
    "base_price_for_client": Decimal("16756.76"),
    "price_adjustment_percent": Decimal("-7.50"),
    "price_for_client": Decimal("15500.00"),
    "additional_expenses": Decimal("650.00"),
    "labor_hours": Decimal("3.50"),
    "amount_paid": Decimal("5000.00"),
}

DEMO_WORK_ITEMS = [
    {
        "work_type": "Циркониевая коронка",
        "description": "Основная реставрация верхнего моляра",
        "quantity": Decimal("1.00"),
        "unit_price": DEMO_WORK_DATA["price_for_client"],
    }
]


def run_migrations() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(backend_root / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(backend_root / "alembic"))
    command.upgrade(alembic_config, "head")


async def ensure_demo_admin() -> str:
    async with SQLAlchemyUnitOfWork() as uow:
        user = await uow.users.get_by_email(DEMO_ADMIN_EMAIL)
        if user is None:
            user = await uow.users.add(
                User(
                    email=DEMO_ADMIN_EMAIL,
                    hashed_password=hash_password(DEMO_ADMIN_PASSWORD),
                    is_active=True,
                )
            )
        else:
            user.hashed_password = hash_password(DEMO_ADMIN_PASSWORD)
            user.is_active = True
        await uow.commit()
        return create_access_token(user.id)


def _apply_client_data(client: Client) -> None:
    client.name = DEMO_CLIENT_DATA["name"]
    client.legal_name = DEMO_CLIENT_DATA["legal_name"]
    client.contact_person = DEMO_CLIENT_DATA["contact_person"]
    client.phone = DEMO_CLIENT_DATA["phone"]
    client.email = DEMO_CLIENT_DATA["email"]
    client.address = DEMO_CLIENT_DATA["address"]
    client.delivery_address = DEMO_CLIENT_DATA["delivery_address"]
    client.delivery_contact = DEMO_CLIENT_DATA["delivery_contact"]
    client.delivery_phone = DEMO_CLIENT_DATA["delivery_phone"]
    client.legal_address = DEMO_CLIENT_DATA["legal_address"]
    client.inn = DEMO_CLIENT_DATA["inn"]
    client.kpp = DEMO_CLIENT_DATA["kpp"]
    client.ogrn = DEMO_CLIENT_DATA["ogrn"]
    client.bank_name = DEMO_CLIENT_DATA["bank_name"]
    client.bik = DEMO_CLIENT_DATA["bik"]
    client.settlement_account = DEMO_CLIENT_DATA["settlement_account"]
    client.correspondent_account = DEMO_CLIENT_DATA["correspondent_account"]
    client.contract_number = DEMO_CLIENT_DATA["contract_number"]
    client.contract_date = DEMO_CLIENT_DATA["contract_date"]
    client.signer_name = DEMO_CLIENT_DATA["signer_name"]
    client.default_price_adjustment_percent = DEMO_CLIENT_DATA["default_price_adjustment_percent"]
    client.comment = DEMO_CLIENT_DATA["comment"]


def _apply_organization_data(profile: OrganizationProfile) -> None:
    for field, value in DEMO_ORGANIZATION_DATA.items():
        setattr(profile, field, value)


def _apply_executor_category_data(category: ExecutorCategory, category_data: dict) -> None:
    category.code = category_data["code"]
    category.name = category_data["name"]
    category.description = category_data["description"]
    category.sort_order = category_data["sort_order"]
    category.is_active = category_data["is_active"]


def _apply_executor_data(executor: Executor, *, category: ExecutorCategory, executor_data: dict) -> None:
    executor.full_name = executor_data["full_name"]
    executor.phone = executor_data["phone"]
    executor.email = executor_data["email"]
    executor.specialization = executor_data["specialization"]
    executor.payment_category_id = category.id
    executor.payment_category = category
    executor.hourly_rate = executor_data["hourly_rate"]
    executor.comment = executor_data["comment"]
    executor.is_active = executor_data["is_active"]


def _apply_doctor_data(doctor: Doctor, *, client: Client, doctor_data: dict) -> None:
    doctor.client_id = client.id
    doctor.client = client
    doctor.full_name = doctor_data["full_name"]
    doctor.phone = doctor_data["phone"]
    doctor.email = doctor_data["email"]
    doctor.specialization = doctor_data["specialization"]
    doctor.comment = doctor_data["comment"]
    doctor.is_active = doctor_data["is_active"]


def _apply_material_data(material: Material) -> None:
    material.name = DEMO_MATERIAL_DATA["name"]
    material.category = DEMO_MATERIAL_DATA["category"]
    material.unit = DEMO_MATERIAL_DATA["unit"]
    material.stock = DEMO_MATERIAL_DATA["stock"]
    material.purchase_price = DEMO_MATERIAL_DATA["purchase_price"]
    material.average_price = DEMO_MATERIAL_DATA["average_price"]
    material.supplier = DEMO_MATERIAL_DATA["supplier"]
    material.min_stock = DEMO_MATERIAL_DATA["min_stock"]
    material.comment = DEMO_MATERIAL_DATA["comment"]


def _apply_operation_data(operation: OperationCatalog, *, category: ExecutorCategory) -> None:
    operation.code = DEMO_OPERATION_DATA["code"]
    operation.name = DEMO_OPERATION_DATA["name"]
    operation.operation_group = DEMO_OPERATION_DATA["operation_group"]
    operation.description = DEMO_OPERATION_DATA["description"]
    operation.default_quantity = DEMO_OPERATION_DATA["default_quantity"]
    operation.default_duration_hours = DEMO_OPERATION_DATA["default_duration_hours"]
    operation.is_active = True
    operation.sort_order = 10

    existing_rates = list(operation.payment_rates)
    primary_rate = next(
        (rate for rate in existing_rates if rate.executor_category_id == category.id),
        existing_rates[0] if existing_rates else None,
    )

    if primary_rate is None:
        operation.payment_rates.append(
            OperationCategoryRate(
                executor_category_id=category.id,
                executor_category=category,
                labor_rate=DEMO_OPERATION_DATA["labor_rate"],
            )
        )
        return

    primary_rate.executor_category_id = category.id
    primary_rate.executor_category = category
    primary_rate.labor_rate = DEMO_OPERATION_DATA["labor_rate"]

    for extra_rate in existing_rates:
        if extra_rate is not primary_rate:
            operation.payment_rates.remove(extra_rate)


def _build_work_catalog_templates(
    catalog_data: dict,
    *,
    operations_by_code: dict[str, OperationCatalog],
) -> list[WorkCatalogItemOperation]:
    rows: list[WorkCatalogItemOperation] = []
    for entry in catalog_data["default_operations"]:
        operation = operations_by_code[entry["operation_code"]]
        rows.append(
            WorkCatalogItemOperation(
                operation_id=operation.id,
                operation=operation,
                quantity=entry["quantity"],
                note=entry["note"],
                sort_order=entry["sort_order"],
            )
        )
    return rows


def _apply_work_catalog_data(
    item: WorkCatalogItem,
    *,
    catalog_data: dict,
    operations_by_code: dict[str, OperationCatalog],
) -> None:
    item.code = catalog_data["code"]
    item.name = catalog_data["name"]
    item.category = catalog_data["category"]
    item.description = catalog_data["description"]
    item.base_price = catalog_data["base_price"]
    item.default_duration_hours = catalog_data["default_duration_hours"]
    item.is_active = catalog_data["is_active"]
    item.sort_order = catalog_data["sort_order"]
    if "default_operations" not in item.__dict__:
        set_committed_value(item, "default_operations", [])
    item.default_operations = _build_work_catalog_templates(catalog_data, operations_by_code=operations_by_code)


def _apply_work_data(
    work: Work,
    *,
    client: Client,
    executor: Executor,
    doctor: Doctor,
    catalog_item: WorkCatalogItem,
) -> None:
    materials_cost = DEMO_MATERIAL_DATA["average_price"]
    labor_cost = DEMO_OPERATION_DATA["labor_rate"] * DEMO_OPERATION_DATA["quantity"]
    total_cost = materials_cost + DEMO_WORK_DATA["additional_expenses"] + labor_cost

    work.order_number = DEMO_WORK_DATA["order_number"]
    work.client_id = client.id
    work.executor_id = executor.id
    work.doctor_id = doctor.id
    work.work_catalog_item_id = catalog_item.id
    work.doctor = doctor
    work.catalog_item = catalog_item
    work.work_type = catalog_item.name
    work.description = DEMO_WORK_DATA["description"]
    work.doctor_name = doctor.full_name
    work.doctor_phone = doctor.phone
    work.patient_name = DEMO_WORK_DATA["patient_name"]
    work.patient_age = DEMO_WORK_DATA["patient_age"]
    work.patient_gender = DEMO_WORK_DATA["patient_gender"]
    work.require_color_photo = DEMO_WORK_DATA["require_color_photo"]
    work.face_shape = DEMO_WORK_DATA["face_shape"]
    work.implant_system = DEMO_WORK_DATA["implant_system"]
    work.metal_type = DEMO_WORK_DATA["metal_type"]
    work.shade_color = DEMO_WORK_DATA["shade_color"]
    work.tooth_selection = DEMO_WORK_DATA["tooth_selection"]
    work.tooth_formula = build_tooth_formula_from_selection(DEMO_WORK_DATA["tooth_selection"])
    work.status = DEMO_WORK_DATA["status"]
    work.received_at = datetime.now(timezone.utc)
    work.deadline_at = datetime.now(timezone.utc) + timedelta(days=3)
    work.completed_at = datetime.now(timezone.utc)
    work.closed_at = work.completed_at
    work.delivery_sent = False
    work.delivery_sent_at = None
    work.base_price_for_client = DEMO_WORK_DATA["base_price_for_client"]
    work.price_adjustment_percent = DEMO_WORK_DATA["price_adjustment_percent"]
    work.price_for_client = DEMO_WORK_DATA["price_for_client"]
    work.additional_expenses = DEMO_WORK_DATA["additional_expenses"]
    work.labor_hours = DEMO_WORK_DATA["labor_hours"]
    work.labor_cost = labor_cost
    work.amount_paid = DEMO_WORK_DATA["amount_paid"]
    work.cost_price = total_cost
    work.margin = DEMO_WORK_DATA["price_for_client"] - total_cost
    if "work_items" not in work.__dict__:
        set_committed_value(work, "work_items", [])
    work.work_items = _build_demo_work_items(catalog_item=catalog_item)


def _apply_work_operation_data(
    work_operation: WorkOperation,
    *,
    work: Work,
    operation: OperationCatalog,
    executor: Executor,
    category: ExecutorCategory,
) -> None:
    work_operation.work_id = work.id
    work_operation.operation_id = operation.id
    work_operation.executor_id = executor.id
    work_operation.executor_category_id = category.id
    work_operation.operation_code = operation.code
    work_operation.operation_name = operation.name
    work_operation.quantity = DEMO_OPERATION_DATA["quantity"]
    work_operation.unit_labor_cost = DEMO_OPERATION_DATA["labor_rate"]
    work_operation.total_labor_cost = DEMO_OPERATION_DATA["labor_rate"] * DEMO_OPERATION_DATA["quantity"]
    work_operation.status = "planned"
    work_operation.sort_order = 0
    work_operation.manual_rate_override = False
    work_operation.note = DEMO_OPERATION_DATA["note"]


def _build_demo_work_items(*, catalog_item: WorkCatalogItem) -> list[WorkItem]:
    return [
        WorkItem(
            work_catalog_item_id=catalog_item.id,
            catalog_item=catalog_item,
            work_type=item["work_type"],
            description=item["description"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            total_price=(item["quantity"] * item["unit_price"]).quantize(Decimal("0.01")),
            sort_order=index,
        )
        for index, item in enumerate(DEMO_WORK_ITEMS)
    ]


def _apply_material_usage_data(work_material: WorkMaterial, *, work: Work, material: Material) -> None:
    quantity = Decimal("1.000")
    unit_cost = material.average_price
    total_cost = unit_cost * quantity

    work_material.work_id = work.id
    work_material.material_id = material.id
    work_material.quantity = quantity
    work_material.unit_cost = unit_cost
    work_material.total_cost = total_cost


def _new_client() -> Client:
    client = Client(
        name=DEMO_CLIENT_DATA["name"],
        legal_name=DEMO_CLIENT_DATA["legal_name"],
        contact_person=DEMO_CLIENT_DATA["contact_person"],
        phone=DEMO_CLIENT_DATA["phone"],
        email=DEMO_CLIENT_DATA["email"],
        address=DEMO_CLIENT_DATA["address"],
        delivery_address=DEMO_CLIENT_DATA["delivery_address"],
        delivery_contact=DEMO_CLIENT_DATA["delivery_contact"],
        delivery_phone=DEMO_CLIENT_DATA["delivery_phone"],
        legal_address=DEMO_CLIENT_DATA["legal_address"],
        inn=DEMO_CLIENT_DATA["inn"],
        kpp=DEMO_CLIENT_DATA["kpp"],
        ogrn=DEMO_CLIENT_DATA["ogrn"],
        bank_name=DEMO_CLIENT_DATA["bank_name"],
        bik=DEMO_CLIENT_DATA["bik"],
        settlement_account=DEMO_CLIENT_DATA["settlement_account"],
        correspondent_account=DEMO_CLIENT_DATA["correspondent_account"],
        contract_number=DEMO_CLIENT_DATA["contract_number"],
        contract_date=DEMO_CLIENT_DATA["contract_date"],
        signer_name=DEMO_CLIENT_DATA["signer_name"],
        default_price_adjustment_percent=DEMO_CLIENT_DATA["default_price_adjustment_percent"],
        comment=DEMO_CLIENT_DATA["comment"],
    )
    return client


def _new_executor(executor_data: dict) -> Executor:
    executor = Executor(
        full_name=executor_data["full_name"],
        phone=executor_data["phone"],
        email=executor_data["email"],
        specialization=executor_data["specialization"],
        hourly_rate=executor_data["hourly_rate"],
        comment=executor_data["comment"],
        is_active=executor_data["is_active"],
    )
    return executor


def _new_doctor(*, client_id: str, doctor_data: dict) -> Doctor:
    return Doctor(
        client_id=client_id,
        full_name=doctor_data["full_name"],
        phone=doctor_data["phone"],
        email=doctor_data["email"],
        specialization=doctor_data["specialization"],
        comment=doctor_data["comment"],
        is_active=doctor_data["is_active"],
    )


def _new_executor_category(category_data: dict) -> ExecutorCategory:
    return ExecutorCategory(
        code=category_data["code"],
        name=category_data["name"],
        description=category_data["description"],
        sort_order=category_data["sort_order"],
        is_active=category_data["is_active"],
    )


def _new_material() -> Material:
    material = Material(
        name=DEMO_MATERIAL_DATA["name"],
        category=DEMO_MATERIAL_DATA["category"],
        unit=DEMO_MATERIAL_DATA["unit"],
        stock=DEMO_MATERIAL_DATA["stock"],
        purchase_price=DEMO_MATERIAL_DATA["purchase_price"],
        average_price=DEMO_MATERIAL_DATA["average_price"],
        supplier=DEMO_MATERIAL_DATA["supplier"],
        min_stock=DEMO_MATERIAL_DATA["min_stock"],
        comment=DEMO_MATERIAL_DATA["comment"],
    )
    return material


def _new_operation(*, category: ExecutorCategory) -> OperationCatalog:
    operation = OperationCatalog(
        code=DEMO_OPERATION_DATA["code"],
        name=DEMO_OPERATION_DATA["name"],
        operation_group=DEMO_OPERATION_DATA["operation_group"],
        description=DEMO_OPERATION_DATA["description"],
        default_quantity=DEMO_OPERATION_DATA["default_quantity"],
        default_duration_hours=DEMO_OPERATION_DATA["default_duration_hours"],
        is_active=True,
        sort_order=10,
    )
    operation.payment_rates = [
        OperationCategoryRate(
            executor_category_id=category.id,
            executor_category=category,
            labor_rate=DEMO_OPERATION_DATA["labor_rate"],
        )
    ]
    return operation


def _new_work(*, client_id: str, executor_id: str, doctor_id: str, catalog_item_id: str) -> Work:
    materials_cost = DEMO_MATERIAL_DATA["average_price"]
    labor_cost = DEMO_OPERATION_DATA["labor_rate"] * DEMO_OPERATION_DATA["quantity"]
    total_cost = materials_cost + DEMO_WORK_DATA["additional_expenses"] + labor_cost

    work = Work(
        order_number=DEMO_WORK_DATA["order_number"],
        client_id=client_id,
        executor_id=executor_id,
        doctor_id=doctor_id,
        work_catalog_item_id=catalog_item_id,
        work_type=DEMO_WORK_CATALOG_FIXTURES[0]["name"],
        description=DEMO_WORK_DATA["description"],
        doctor_name=DEMO_DOCTOR_FIXTURES[0]["full_name"],
        doctor_phone=DEMO_DOCTOR_FIXTURES[0]["phone"],
        patient_name=DEMO_WORK_DATA["patient_name"],
        patient_age=DEMO_WORK_DATA["patient_age"],
        patient_gender=DEMO_WORK_DATA["patient_gender"],
        require_color_photo=DEMO_WORK_DATA["require_color_photo"],
        face_shape=DEMO_WORK_DATA["face_shape"],
        implant_system=DEMO_WORK_DATA["implant_system"],
        metal_type=DEMO_WORK_DATA["metal_type"],
        shade_color=DEMO_WORK_DATA["shade_color"],
        tooth_selection=DEMO_WORK_DATA["tooth_selection"],
        tooth_formula=build_tooth_formula_from_selection(DEMO_WORK_DATA["tooth_selection"]),
        status=DEMO_WORK_DATA["status"],
        received_at=datetime.now(timezone.utc),
        deadline_at=datetime.now(timezone.utc) + timedelta(days=3),
        completed_at=datetime.now(timezone.utc),
        closed_at=datetime.now(timezone.utc),
        delivery_sent=False,
        delivery_sent_at=None,
        base_price_for_client=DEMO_WORK_DATA["base_price_for_client"],
        price_adjustment_percent=DEMO_WORK_DATA["price_adjustment_percent"],
        price_for_client=DEMO_WORK_DATA["price_for_client"],
        additional_expenses=DEMO_WORK_DATA["additional_expenses"],
        labor_hours=DEMO_WORK_DATA["labor_hours"],
        labor_cost=labor_cost,
        amount_paid=DEMO_WORK_DATA["amount_paid"],
        cost_price=total_cost,
        margin=DEMO_WORK_DATA["price_for_client"] - total_cost,
    )
    return work


async def ensure_demo_entities(
    search: SearchService, cache: CacheService
) -> tuple[OrganizationProfile, Client, Executor, Material, Work, Doctor, WorkCatalogItem]:
    async with SQLAlchemyUnitOfWork() as uow:
        organization = await uow.organization.get_profile()
        if organization is None:
            organization = await uow.organization.add_profile(OrganizationProfile(**DEMO_ORGANIZATION_DATA))

        categories_by_code: dict[str, ExecutorCategory] = {}
        for executor_fixture in DEMO_EXECUTOR_FIXTURES:
            category_data = executor_fixture["payment_category"]
            category = categories_by_code.get(category_data["code"])
            if category is None:
                category = await uow.operations.get_category_by_code(category_data["code"])
                if category is None:
                    category = await uow.operations.add_category(_new_executor_category(category_data))
                categories_by_code[category_data["code"]] = category
            _apply_executor_category_data(category, category_data)

        primary_category = categories_by_code[DEMO_EXECUTOR_CATEGORY_DATA["code"]]

        operation = await uow.operations.get_operation_by_code(DEMO_OPERATION_DATA["code"])
        if operation is None:
            operation = await uow.operations.add_operation(_new_operation(category=primary_category))

        work_summary = await uow.works.get_by_order_number(DEMO_WORK_ORDER_NUMBER)
        work = await uow.works.get(work_summary.id) if work_summary else None
        work_existed = work is not None

        executors: list[Executor] = []
        for executor_fixture in DEMO_EXECUTOR_FIXTURES:
            result = await uow.session.execute(
                select(Executor)
                .options(selectinload(Executor.payment_category))
                .where(Executor.email == executor_fixture["email"])
            )
            executor = result.scalar_one_or_none()
            if executor is None:
                executor = await uow.executors.add(_new_executor(executor_fixture))
            category = categories_by_code[executor_fixture["payment_category"]["code"]]
            _apply_executor_data(executor, category=category, executor_data=executor_fixture)
            executors.append(executor)

        primary_executor = executors[0]

        if work is not None:
            client = work.client
            if client is None:
                client = await uow.clients.add(_new_client())

            material_usage = work.materials[0] if work.materials else None
            material = material_usage.material if material_usage and material_usage.material else None
            if material is None:
                material = await uow.materials.add(_new_material())

            if material_usage is None:
                material_usage = await uow.works.add_material_usage(
                    WorkMaterial(work_id=work.id, material_id=material.id)
                )
            work_operation = work.work_operations[0] if work.work_operations else None
            work_operation_existed = work_operation is not None
            if work_operation is None:
                work_operation = await uow.operations.add_work_operation(
                    WorkOperation(work_id=work.id, operation_id=operation.id, operation_name=operation.name)
                )

            for extra_material in work.materials[1:]:
                await uow.session.delete(extra_material)
            for extra_operation in work.work_operations[1:]:
                await uow.session.delete(extra_operation)
            for existing_work_item in list(work.work_items):
                await uow.session.delete(existing_work_item)
            await uow.session.flush()
        else:
            client = await uow.clients.add(_new_client())
            material = await uow.materials.add(_new_material())
            work = None
            material_usage = None
            work_operation = None
            work_operation_existed = False

        _apply_organization_data(organization)
        _apply_client_data(client)
        _apply_operation_data(operation, category=primary_category)

        doctors: list[Doctor] = []
        for doctor_fixture in DEMO_DOCTOR_FIXTURES:
            result = await uow.session.execute(select(Doctor).where(Doctor.email == doctor_fixture["email"]))
            doctor = result.scalar_one_or_none()
            if doctor is None:
                doctor = await uow.doctors.add(_new_doctor(client_id=client.id, doctor_data=doctor_fixture))
            _apply_doctor_data(doctor, client=client, doctor_data=doctor_fixture)
            doctors.append(doctor)

        operations_by_code = {operation.code: operation}
        catalog_items: list[WorkCatalogItem] = []
        for catalog_fixture in DEMO_WORK_CATALOG_FIXTURES:
            catalog_item = await uow.work_catalog.get_by_code(catalog_fixture["code"])
            if catalog_item is None:
                catalog_item = await uow.work_catalog.add(
                    WorkCatalogItem(
                        code=catalog_fixture["code"],
                        name=catalog_fixture["name"],
                        category=catalog_fixture["category"],
                        description=catalog_fixture["description"],
                        base_price=catalog_fixture["base_price"],
                        default_duration_hours=catalog_fixture["default_duration_hours"],
                        is_active=catalog_fixture["is_active"],
                        sort_order=catalog_fixture["sort_order"],
                    )
                )
            existing_templates = (
                await uow.session.execute(
                    select(WorkCatalogItemOperation).where(WorkCatalogItemOperation.catalog_item_id == catalog_item.id)
                )
            ).scalars().all()
            for existing_template in existing_templates:
                await uow.session.delete(existing_template)
            await uow.session.flush()
            _apply_work_catalog_data(
                catalog_item,
                catalog_data=catalog_fixture,
                operations_by_code=operations_by_code,
            )
            catalog_items.append(catalog_item)

        catalog_items_by_code = {item.code: item for item in catalog_items}
        existing_catalog_prices = (
            await uow.session.execute(
                select(ClientWorkCatalogPrice).where(ClientWorkCatalogPrice.client_id == client.id)
            )
        ).scalars().all()
        for existing_catalog_price in existing_catalog_prices:
            await uow.session.delete(existing_catalog_price)
        await uow.session.flush()
        if "catalog_prices" not in client.__dict__:
            set_committed_value(client, "catalog_prices", [])
        client.catalog_prices = [
            ClientWorkCatalogPrice(
                work_catalog_item_id=catalog_items_by_code[price_fixture["code"]].id,
                price=price_fixture["price"],
                comment=price_fixture["comment"],
                catalog_item=catalog_items_by_code[price_fixture["code"]],
            )
            for price_fixture in DEMO_CLIENT_CATALOG_PRICES
            if price_fixture["code"] in catalog_items_by_code
        ]

        primary_doctor = doctors[0]
        primary_catalog_item = catalog_items[0]
        if work is None:
            work = await uow.works.add(
                _new_work(
                    client_id=client.id,
                    executor_id=primary_executor.id,
                    doctor_id=primary_doctor.id,
                    catalog_item_id=primary_catalog_item.id,
                )
            )
            material_usage = await uow.works.add_material_usage(
                WorkMaterial(work_id=work.id, material_id=material.id)
            )
            work_operation = await uow.operations.add_work_operation(
                WorkOperation(work_id=work.id, operation_id=operation.id, operation_name=operation.name)
            )
        _apply_material_data(material)
        _apply_work_data(
            work,
            client=client,
            executor=primary_executor,
            doctor=primary_doctor,
            catalog_item=primary_catalog_item,
        )
        _apply_work_operation_data(
            work_operation,
            work=work,
            operation=operation,
            executor=primary_executor,
            category=primary_category,
        )
        _apply_material_usage_data(material_usage, work=work, material=material)

        if work_operation_existed:
            for log in list(work_operation.logs):
                await uow.session.delete(log)
        await uow.operations.add_work_operation_log(
            WorkOperationLog(
                work_operation_id=work_operation.id,
                action="seeded",
                actor_email=DEMO_ADMIN_EMAIL,
                details={
                    "operation_name": work_operation.operation_name,
                    "quantity": str(work_operation.quantity),
                    "unit_labor_cost": str(work_operation.unit_labor_cost),
                    "total_labor_cost": str(work_operation.total_labor_cost),
                },
            )
        )
        if work_existed:
            for log in list(work.change_logs):
                await uow.session.delete(log)
        await uow.works.add_change_log(
            WorkChangeLog(
                work_id=work.id,
                action="seeded",
                actor_email=DEMO_ADMIN_EMAIL,
                details={
                    "patient_name": work.patient_name,
                    "doctor_name": work.doctor_name,
                    "doctor_phone": work.doctor_phone,
                    "tooth_formula": work.tooth_formula,
                    "price_adjustment_percent": str(work.price_adjustment_percent),
                    "price_for_client": str(work.price_for_client),
                },
            )
        )

        await uow.commit()

    await search.index_document(
        settings.elasticsearch_clients_index,
        client.id,
        build_client_search_document(client),
    )
    await search.index_document(
        settings.elasticsearch_executors_index,
        primary_executor.id,
        build_executor_search_document(primary_executor),
    )
    for doctor in doctors:
        await search.index_document(
            settings.elasticsearch_doctors_index,
            doctor.id,
            build_doctor_search_document(doctor),
        )
    for executor in executors[1:]:
        await search.index_document(
            settings.elasticsearch_executors_index,
            executor.id,
            build_executor_search_document(executor),
        )
    for catalog_item in catalog_items:
        await search.index_document(
            settings.elasticsearch_work_catalog_index,
            catalog_item.id,
            build_work_catalog_search_document(catalog_item),
        )
    await search.index_document(
        settings.elasticsearch_operations_index,
        operation.id,
        build_operation_search_document(operation),
    )
    await search.index_document(
        settings.elasticsearch_materials_index,
        material.id,
        build_material_search_document(material),
    )
    await search.index_document(
        settings.elasticsearch_works_index,
        work.id,
        build_work_search_document(
            work,
            client_name=client.name,
            executor_name=primary_executor.full_name,
            doctor_name=primary_doctor.full_name,
            work_catalog_item_name=primary_catalog_item.name,
            work_catalog_item_code=primary_catalog_item.code,
            work_catalog_item_category=primary_catalog_item.category,
            operation_names=[operation.name],
            material_names=[material.name],
        ),
    )
    await cache.invalidate_prefix("dashboard:")

    return organization, client, primary_executor, material, work, primary_doctor, primary_catalog_item


async def seed() -> None:
    cache = CacheService(redis_client)
    search = SearchService(search_client)

    try:
        await search.ensure_indices()

        auth_token = await ensure_demo_admin()
        organization, client, executor, material, work, doctor, catalog_item = await ensure_demo_entities(search, cache)

        print("Seed завершен. Тестовые данные обновлены.")
        print(f"Администратор: {DEMO_ADMIN_EMAIL}")
        print(f"Пароль: {DEMO_ADMIN_PASSWORD}")
        print(f"Тестовый клиент: {client.name}")
        print(f"Текущая организация: {organization.legal_name}")
        print(f"Тестовый исполнитель: {executor.full_name}")
        print(f"Тестовый врач: {doctor.full_name}")
        print(f"Тестовая позиция каталога: {catalog_item.name}")
        print(f"Тестовый материал: {material.name}")
        print(f"Тестовая работа: {work.order_number}")
        print(f"Префикс токена доступа: {auth_token[:12]}")
    finally:
        await redis_client.aclose()
        await search_client.close()
        await engine.dispose()


if __name__ == "__main__":
    run_migrations()
    asyncio.run(seed())
