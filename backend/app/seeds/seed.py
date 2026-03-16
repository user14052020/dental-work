from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.common.enums import MaterialUnit, WorkStatus
from app.common.search_documents import (
    build_client_search_document,
    build_executor_search_document,
    build_material_search_document,
    build_work_search_document,
)
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.resources import redis_client, search_client
from app.core.security import create_access_token, hash_password
from app.db.engine import engine
from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.material import Material
from app.db.models.user import User
from app.db.models.work import Work, WorkMaterial
from app.db.unitofwork import SQLAlchemyUnitOfWork


DEMO_ADMIN_EMAIL = "admin@dentallab.app"
DEMO_ADMIN_PASSWORD = "admin123"
DEMO_WORK_ORDER_NUMBER = "DL-2026-0001"

DEMO_CLIENT_DATA = {
    "name": "Клиника Улыбка",
    "contact_person": "Анна Петрова",
    "phone": "+79991234567",
    "email": "anna@ulybka-clinic.ru",
    "address": "Москва, ул. Тверская, 1",
    "comment": "Приоритетный клиент лаборатории",
}

DEMO_EXECUTOR_DATA = {
    "full_name": "Дмитрий Иванов",
    "phone": "+79990001122",
    "email": "d.ivanov@dentallab.app",
    "specialization": "Керамика",
    "hourly_rate": Decimal("2800.00"),
    "comment": "Старший техник по керамике",
    "is_active": True,
}

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

DEMO_WORK_DATA = {
    "order_number": DEMO_WORK_ORDER_NUMBER,
    "work_type": "Циркониевая коронка",
    "description": "Восстановление верхнего моляра",
    "status": WorkStatus.NEW.value,
    "price_for_client": Decimal("15500.00"),
    "additional_expenses": Decimal("650.00"),
    "labor_hours": Decimal("3.50"),
    "amount_paid": Decimal("5000.00"),
    "comment": "Срочный заказ для постоянного клиента",
}


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
    client.contact_person = DEMO_CLIENT_DATA["contact_person"]
    client.phone = DEMO_CLIENT_DATA["phone"]
    client.email = DEMO_CLIENT_DATA["email"]
    client.address = DEMO_CLIENT_DATA["address"]
    client.comment = DEMO_CLIENT_DATA["comment"]


def _apply_executor_data(executor: Executor) -> None:
    executor.full_name = DEMO_EXECUTOR_DATA["full_name"]
    executor.phone = DEMO_EXECUTOR_DATA["phone"]
    executor.email = DEMO_EXECUTOR_DATA["email"]
    executor.specialization = DEMO_EXECUTOR_DATA["specialization"]
    executor.hourly_rate = DEMO_EXECUTOR_DATA["hourly_rate"]
    executor.comment = DEMO_EXECUTOR_DATA["comment"]
    executor.is_active = DEMO_EXECUTOR_DATA["is_active"]


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


def _apply_work_data(work: Work, *, client: Client, executor: Executor) -> None:
    materials_cost = DEMO_MATERIAL_DATA["average_price"]
    labor_cost = DEMO_WORK_DATA["labor_hours"] * DEMO_EXECUTOR_DATA["hourly_rate"]
    total_cost = materials_cost + DEMO_WORK_DATA["additional_expenses"] + labor_cost

    work.order_number = DEMO_WORK_DATA["order_number"]
    work.client_id = client.id
    work.executor_id = executor.id
    work.work_type = DEMO_WORK_DATA["work_type"]
    work.description = DEMO_WORK_DATA["description"]
    work.status = DEMO_WORK_DATA["status"]
    work.received_at = datetime.now(timezone.utc)
    work.deadline_at = datetime.now(timezone.utc) + timedelta(days=3)
    work.completed_at = None
    work.price_for_client = DEMO_WORK_DATA["price_for_client"]
    work.additional_expenses = DEMO_WORK_DATA["additional_expenses"]
    work.labor_hours = DEMO_WORK_DATA["labor_hours"]
    work.amount_paid = DEMO_WORK_DATA["amount_paid"]
    work.cost_price = total_cost
    work.margin = DEMO_WORK_DATA["price_for_client"] - total_cost
    work.comment = DEMO_WORK_DATA["comment"]


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
        contact_person=DEMO_CLIENT_DATA["contact_person"],
        phone=DEMO_CLIENT_DATA["phone"],
        email=DEMO_CLIENT_DATA["email"],
        address=DEMO_CLIENT_DATA["address"],
        comment=DEMO_CLIENT_DATA["comment"],
    )
    return client


def _new_executor() -> Executor:
    executor = Executor(
        full_name=DEMO_EXECUTOR_DATA["full_name"],
        phone=DEMO_EXECUTOR_DATA["phone"],
        email=DEMO_EXECUTOR_DATA["email"],
        specialization=DEMO_EXECUTOR_DATA["specialization"],
        hourly_rate=DEMO_EXECUTOR_DATA["hourly_rate"],
        comment=DEMO_EXECUTOR_DATA["comment"],
        is_active=DEMO_EXECUTOR_DATA["is_active"],
    )
    return executor


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


def _new_work(*, client_id: str, executor_id: str) -> Work:
    materials_cost = DEMO_MATERIAL_DATA["average_price"]
    labor_cost = DEMO_WORK_DATA["labor_hours"] * DEMO_EXECUTOR_DATA["hourly_rate"]
    total_cost = materials_cost + DEMO_WORK_DATA["additional_expenses"] + labor_cost

    work = Work(
        order_number=DEMO_WORK_DATA["order_number"],
        client_id=client_id,
        executor_id=executor_id,
        work_type=DEMO_WORK_DATA["work_type"],
        description=DEMO_WORK_DATA["description"],
        status=DEMO_WORK_DATA["status"],
        received_at=datetime.now(timezone.utc),
        deadline_at=datetime.now(timezone.utc) + timedelta(days=3),
        price_for_client=DEMO_WORK_DATA["price_for_client"],
        additional_expenses=DEMO_WORK_DATA["additional_expenses"],
        labor_hours=DEMO_WORK_DATA["labor_hours"],
        amount_paid=DEMO_WORK_DATA["amount_paid"],
        cost_price=total_cost,
        margin=DEMO_WORK_DATA["price_for_client"] - total_cost,
        comment=DEMO_WORK_DATA["comment"],
    )
    return work


async def ensure_demo_entities(search: SearchService, cache: CacheService) -> tuple[Client, Executor, Material, Work]:
    async with SQLAlchemyUnitOfWork() as uow:
        work_summary = await uow.works.get_by_order_number(DEMO_WORK_ORDER_NUMBER)
        work = await uow.works.get(work_summary.id) if work_summary else None

        if work is not None:
            client = work.client
            if client is None:
                client = await uow.clients.add(_new_client())

            executor = work.executor
            if executor is None:
                executor = await uow.executors.add(_new_executor())

            material_usage = work.materials[0] if work.materials else None
            material = material_usage.material if material_usage and material_usage.material else None
            if material is None:
                material = await uow.materials.add(_new_material())

            if material_usage is None:
                material_usage = await uow.works.add_material_usage(
                    WorkMaterial(work_id=work.id, material_id=material.id)
                )

            for extra_material in work.materials[1:]:
                await uow.session.delete(extra_material)
        else:
            client = await uow.clients.add(_new_client())
            executor = await uow.executors.add(_new_executor())
            material = await uow.materials.add(_new_material())
            work = await uow.works.add(_new_work(client_id=client.id, executor_id=executor.id))
            material_usage = await uow.works.add_material_usage(
                WorkMaterial(work_id=work.id, material_id=material.id)
            )

        _apply_client_data(client)
        _apply_executor_data(executor)
        _apply_material_data(material)
        _apply_work_data(work, client=client, executor=executor)
        _apply_material_usage_data(material_usage, work=work, material=material)

        await uow.commit()

    await search.index_document(
        settings.elasticsearch_clients_index,
        client.id,
        build_client_search_document(client),
    )
    await search.index_document(
        settings.elasticsearch_executors_index,
        executor.id,
        build_executor_search_document(executor),
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
            executor_name=executor.full_name,
            material_names=[material.name],
        ),
    )
    await cache.invalidate_prefix("dashboard:")

    return client, executor, material, work


async def seed() -> None:
    cache = CacheService(redis_client)
    search = SearchService(search_client)

    try:
        await search.ensure_indices()

        auth_token = await ensure_demo_admin()
        client, executor, material, work = await ensure_demo_entities(search, cache)

        print("Seed завершен. Тестовые данные обновлены.")
        print(f"Администратор: {DEMO_ADMIN_EMAIL}")
        print(f"Пароль: {DEMO_ADMIN_PASSWORD}")
        print(f"Тестовый клиент: {client.name}")
        print(f"Тестовый исполнитель: {executor.full_name}")
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
