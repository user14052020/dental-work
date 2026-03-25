from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.permissions import ADMIN_PERMISSION, has_permission, normalize_permission_codes
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.db.models.user import User
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.auth.schemas import UserRead
from app.modules.employees.schemas import EmployeeCreate, EmployeeListResponse, EmployeeRead, EmployeeUpdate


class EmployeeService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    @staticmethod
    def _build_employee_read(user: User) -> EmployeeRead:
        return EmployeeRead.model_validate(user).model_copy(
            update={
                "executor_name": user.executor.full_name if getattr(user, "executor", None) else None,
                "is_technician": bool(getattr(user, "executor_id", None)),
            }
        )

    async def list_employees(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        include_fired: bool,
    ) -> EmployeeListResponse:
        async with self._uow as uow:
            users, total_items = await uow.users.list(
                page=page,
                page_size=page_size,
                search=search,
                include_fired=include_fired,
            )
            items = [self._build_employee_read(user) for user in users]
        return PaginatedResponse[EmployeeRead].create(items, page=page, page_size=page_size, total_items=total_items)

    async def get_employee(self, employee_id: str) -> EmployeeRead:
        async with self._uow as uow:
            user = await uow.users.get_by_id(employee_id)
            if user is None:
                raise NotFoundError("employee", employee_id)
            return self._build_employee_read(user)

    async def create_employee(self, payload: EmployeeCreate, *, current_user: UserRead) -> EmployeeRead:
        self._ensure_permissions_edit_allowed(current_user, payload.permission_codes)
        async with self._uow as uow:
            existing_user = await uow.users.get_by_email(payload.email)
            if existing_user is not None:
                raise ConflictError("User with this email already exists.", code="email_already_registered")
            await self._ensure_executor_link_is_available(uow, payload.executor_id)
            user = await uow.users.add(
                User(
                    full_name=payload.full_name,
                    email=payload.email,
                    phone=payload.phone,
                    job_title=payload.job_title,
                    hashed_password=hash_password(payload.password),
                    is_active=payload.is_active,
                    is_fired=payload.is_fired,
                    executor_id=payload.executor_id,
                    permission_codes=normalize_permission_codes(payload.permission_codes),
                )
            )
            await uow.commit()
            return self._build_employee_read(user)

    async def update_employee(self, employee_id: str, payload: EmployeeUpdate, *, current_user: UserRead) -> EmployeeRead:
        self._ensure_permissions_edit_allowed(current_user, payload.permission_codes)
        async with self._uow as uow:
            user = await uow.users.get_by_id(employee_id)
            if user is None:
                raise NotFoundError("employee", employee_id)

            data = payload.model_dump(exclude_unset=True)

            if user.id == current_user.id:
                if data.get("is_active") is False or data.get("is_fired") is True:
                    raise ConflictError(
                        "You cannot deactivate or fire your own account.",
                        code="employee_self_disable_forbidden",
                    )
                if "permission_codes" in data:
                    raise ConflictError(
                        "You cannot change your own permissions.",
                        code="employee_self_permissions_forbidden",
                    )

            if "email" in data and data["email"] != user.email:
                existing_user = await uow.users.get_by_email(data["email"])
                if existing_user is not None and existing_user.id != user.id:
                    raise ConflictError("User with this email already exists.", code="email_already_registered")

            if "executor_id" in data:
                await self._ensure_executor_link_is_available(uow, data["executor_id"], exclude_user_id=user.id)

            if "permission_codes" in data:
                data["permission_codes"] = normalize_permission_codes(data["permission_codes"])

            if "password" in data:
                password = data.pop("password")
                if password:
                    user.hashed_password = hash_password(password)

            for field, value in data.items():
                setattr(user, field, value)

            await uow.commit()
            return self._build_employee_read(user)

    @staticmethod
    async def _ensure_executor_link_is_available(
        uow: SQLAlchemyUnitOfWork,
        executor_id: str | None,
        *,
        exclude_user_id: str | None = None,
    ) -> None:
        if executor_id is None:
            return
        executor = await uow.executors.get(executor_id)
        if executor is None:
            raise NotFoundError("executor", executor_id)
        linked_user = await uow.users.get_by_executor_id(executor_id)
        if linked_user is not None and linked_user.id != exclude_user_id:
            raise ConflictError(
                "This technician is already linked to another employee.",
                code="executor_already_linked_to_employee",
            )

    @staticmethod
    def _ensure_permissions_edit_allowed(current_user: UserRead, permission_codes: list[str] | None) -> None:
        if permission_codes is None:
            return
        normalized = normalize_permission_codes(permission_codes)
        if normalized and not (
            has_permission(current_user.permission_codes, "permissions.manage")
            or has_permission(current_user.permission_codes, ADMIN_PERMISSION)
        ):
            raise AuthorizationError("You are not allowed to assign permissions.")
