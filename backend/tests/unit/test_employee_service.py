from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import pytest

from app.core.exceptions import AuthorizationError, ConflictError
from app.modules.auth.schemas import UserRead
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate
from app.modules.employees.service import EmployeeService


@dataclass
class FakeExecutor:
    id: str
    full_name: str


@dataclass
class FakeUser:
    id: str
    full_name: str
    email: str
    hashed_password: str
    phone: str | None = None
    job_title: str | None = None
    is_active: bool = True
    is_fired: bool = False
    permission_codes: list[str] = field(default_factory=list)
    executor_id: str | None = None
    executor: FakeExecutor | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FakeUserRepository:
    def __init__(self):
        self.items: dict[str, FakeUser] = {}

    async def get_by_email(self, email: str):
        return next((user for user in self.items.values() if user.email == email), None)

    async def get_by_id(self, user_id: str):
        return self.items.get(user_id)

    async def get_by_executor_id(self, executor_id: str):
        return next((user for user in self.items.values() if user.executor_id == executor_id), None)

    async def list(self, *, page, page_size, search=None, include_fired=False):
        values = list(self.items.values())
        if not include_fired:
            values = [item for item in values if not item.is_fired]
        return values, len(values)

    async def add(self, user):
        fake = FakeUser(
            id=str(uuid4()),
            full_name=user.full_name,
            email=user.email,
            hashed_password=user.hashed_password,
            phone=user.phone,
            job_title=user.job_title,
            is_active=user.is_active,
            is_fired=user.is_fired,
            permission_codes=list(user.permission_codes),
            executor_id=user.executor_id,
            executor=None,
        )
        self.items[fake.id] = fake
        return fake


class FakeExecutorRepository:
    def __init__(self, executor: FakeExecutor):
        self.executor = executor

    async def get(self, executor_id: str):
        return self.executor if self.executor.id == executor_id else None


class FakeContextUow:
    def __init__(self, executor: FakeExecutor):
        self.users = FakeUserRepository()
        self.executors = FakeExecutorRepository(executor)
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


def build_current_user(permission_codes: list[str]) -> UserRead:
    now = datetime.now(timezone.utc)
    return UserRead(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        full_name="Manager",
        email="manager@example.com",
        phone=None,
        job_title="Менеджер",
        is_active=True,
        is_fired=False,
        permission_codes=permission_codes,
        executor_id=None,
        executor_name=None,
        is_technician=False,
    )


@pytest.mark.asyncio
async def test_create_employee_rejects_permission_assignment_without_manage_permissions():
    executor = FakeExecutor(id=str(uuid4()), full_name="Дмитрий Иванов")
    service = EmployeeService(FakeContextUow(executor))

    with pytest.raises(AuthorizationError):
        await service.create_employee(
            EmployeeCreate(
                full_name="Новый сотрудник",
                email="user@example.com",
                password="password123",
                permission_codes=["reports.view"],
            ),
            current_user=build_current_user(["employees.manage"]),
        )


@pytest.mark.asyncio
async def test_create_employee_links_executor_and_normalizes_permissions():
    executor = FakeExecutor(id=str(uuid4()), full_name="Дмитрий Иванов")
    uow = FakeContextUow(executor)
    service = EmployeeService(uow)

    result = await service.create_employee(
        EmployeeCreate(
            full_name="Техник Иванов",
            email="tech@example.com",
            password="password123",
            executor_id=executor.id,
            permission_codes=["reports.view", "reports.view", "unknown"],
        ),
        current_user=build_current_user(["employees.manage", "permissions.manage"]),
    )

    assert uow.committed is True
    assert result.executor_id == executor.id
    assert result.permission_codes == ["reports.view"]
    stored = next(iter(uow.users.items.values()))
    assert stored.hashed_password != "password123"


@pytest.mark.asyncio
async def test_update_employee_cannot_disable_self():
    executor = FakeExecutor(id=str(uuid4()), full_name="Дмитрий Иванов")
    uow = FakeContextUow(executor)
    service = EmployeeService(uow)
    current_user = build_current_user(["*"])
    existing = FakeUser(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        hashed_password="hashed",
        permission_codes=["*"],
    )
    uow.users.items[existing.id] = existing

    with pytest.raises(ConflictError):
        await service.update_employee(existing.id, EmployeeUpdate(is_active=False), current_user=current_user)
