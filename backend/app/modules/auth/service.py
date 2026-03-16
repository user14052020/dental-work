from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_token_expiration,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.auth.schemas import AuthTokenRead, LoginRequest, RefreshTokenRequest, RegisterRequest, UserRead


class AuthService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def register(self, payload: RegisterRequest) -> AuthTokenRead:
        async with self._uow as uow:
            existing_user = await uow.users.get_by_email(payload.email)
            if existing_user:
                raise ConflictError("User with this email already exists.", code="email_already_registered")
            user = await uow.users.add(
                User(email=payload.email, hashed_password=hash_password(payload.password), is_active=True)
            )
            session = await self._issue_session(uow, user)
            await uow.commit()
            return session

    async def login(self, payload: LoginRequest) -> AuthTokenRead:
        async with self._uow as uow:
            user = await uow.users.get_by_email(payload.email)
            if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
                raise AuthenticationError()
            session = await self._issue_session(uow, user)
            await uow.commit()
            return session

    async def refresh(self, payload: RefreshTokenRequest) -> AuthTokenRead:
        token_payload = decode_refresh_token(payload.refresh_token)
        token_jti = token_payload["jti"]

        async with self._uow as uow:
            stored_token = await uow.refresh_tokens.get_by_jti(token_jti)
            if stored_token is None:
                raise AuthenticationError("Refresh session was not found.")
            if stored_token.revoked_at is not None:
                raise AuthenticationError("Refresh session has been revoked.")
            if stored_token.expires_at <= datetime.now(timezone.utc):
                raise AuthenticationError("Refresh token is expired.")
            if not verify_token_hash(payload.refresh_token, stored_token.token_hash):
                raise AuthenticationError("Refresh token does not match the active session.")

            user = await uow.users.get_by_id(token_payload["sub"])
            if user is None or not user.is_active:
                raise AuthenticationError()

            await uow.refresh_tokens.revoke(stored_token)
            session = await self._issue_session(uow, user)
            await uow.commit()
            return session

    async def logout(self, payload: RefreshTokenRequest) -> None:
        try:
            token_payload = decode_refresh_token(payload.refresh_token)
        except AuthenticationError:
            return

        async with self._uow as uow:
            stored_token = await uow.refresh_tokens.get_by_jti(token_payload["jti"])
            if stored_token is not None and stored_token.revoked_at is None:
                await uow.refresh_tokens.revoke(stored_token)
                await uow.commit()

    async def get_current_user(self, user_id: str) -> UserRead:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise NotFoundError("user", user_id)
            if not user.is_active:
                raise AuthenticationError()
            return UserRead.model_validate(user)

    async def _issue_session(self, uow: SQLAlchemyUnitOfWork, user: User) -> AuthTokenRead:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        refresh_payload = decode_refresh_token(refresh_token)
        await uow.refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                token_jti=refresh_payload["jti"],
                token_hash=hash_token(refresh_token),
                expires_at=get_token_expiration(refresh_payload),
            )
        )
        return AuthTokenRead(
            accessToken=access_token,
            refreshToken=refresh_token,
            user=UserRead.model_validate(user),
        )
