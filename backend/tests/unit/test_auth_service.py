from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.modules.auth.schemas import RefreshTokenRequest, RegisterRequest
from app.modules.auth.service import AuthService


@dataclass
class FakeUser:
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FakeRefreshToken:
    user_id: str
    token_jti: str
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None


class FakeUserRepository:
    def __init__(self):
        self.items: dict[str, FakeUser] = {}

    async def get_by_email(self, email: str) -> FakeUser | None:
        return next((user for user in self.items.values() if user.email == email), None)

    async def get_by_id(self, user_id: str) -> FakeUser | None:
        return self.items.get(user_id)

    async def add(self, user) -> FakeUser:
        fake = FakeUser(
            id=str(uuid4()),
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=getattr(user, "is_active", True),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.items[fake.id] = fake
        return fake


class FakeRefreshTokenRepository:
    def __init__(self):
        self.items: dict[str, FakeRefreshToken] = {}

    async def add(self, refresh_token) -> FakeRefreshToken:
        fake = FakeRefreshToken(
            user_id=refresh_token.user_id,
            token_jti=refresh_token.token_jti,
            token_hash=refresh_token.token_hash,
            expires_at=refresh_token.expires_at,
            revoked_at=refresh_token.revoked_at,
        )
        self.items[fake.token_jti] = fake
        return fake

    async def get_by_jti(self, token_jti: str) -> FakeRefreshToken | None:
        return self.items.get(token_jti)

    async def revoke(self, refresh_token: FakeRefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)


class FakeContextUoW:
    def __init__(self):
        self.users = FakeUserRepository()
        self.refresh_tokens = FakeRefreshTokenRepository()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_register_returns_access_and_refresh_tokens():
    service = AuthService(uow=FakeContextUoW())

    session = await service.register(
        RegisterRequest(email="admin@example.com", password="admin123")
    )

    assert session.access_token
    assert session.refresh_token
    assert session.user.email == "admin@example.com"


@pytest.mark.asyncio
async def test_refresh_rotates_refresh_token():
    uow = FakeContextUoW()
    service = AuthService(uow=uow)

    initial_session = await service.register(
        RegisterRequest(email="owner@example.com", password="admin123")
    )

    initial_record = next(iter(uow.refresh_tokens.items.values()))
    assert initial_record.revoked_at is None

    refreshed_session = await service.refresh(
        RefreshTokenRequest(refreshToken=initial_session.refresh_token)
    )

    assert refreshed_session.access_token != initial_session.access_token
    assert refreshed_session.refresh_token != initial_session.refresh_token
    assert initial_record.revoked_at is not None
    assert len(uow.refresh_tokens.items) == 2


@pytest.mark.asyncio
async def test_logout_revokes_active_refresh_token():
    uow = FakeContextUoW()
    service = AuthService(uow=uow)
    session = await service.register(
        RegisterRequest(email="logout@example.com", password="admin123")
    )

    await service.logout(RefreshTokenRequest(refreshToken=session.refresh_token))

    stored = next(iter(uow.refresh_tokens.items.values()))
    assert stored.revoked_at is not None
