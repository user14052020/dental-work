from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.executor import Executor
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.executor)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.executor)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_executor_id(self, executor_id: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.executor)).where(User.executor_id == executor_id)
        )
        return result.scalar_one_or_none()

    async def count(self) -> int:
        return int(await self.session.scalar(select(func.count(User.id))) or 0)

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        include_fired: bool = False,
    ) -> tuple[list[User], int]:
        stmt = (
            select(User)
            .options(selectinload(User.executor))
            .outerjoin(Executor, User.executor_id == Executor.id)
            .order_by(User.created_at.desc())
        )
        count_stmt = select(func.count(User.id)).select_from(User).outerjoin(Executor, User.executor_id == Executor.id)

        if search:
            filter_expression = or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
                User.job_title.ilike(f"%{search}%"),
                Executor.full_name.ilike(f"%{search}%"),
                Executor.specialization.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if not include_fired:
            stmt = stmt.where(User.is_fired.is_(False))
            count_stmt = count_stmt.where(User.is_fired.is_(False))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_by_jti(self, token_jti: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_jti == token_jti)
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()
