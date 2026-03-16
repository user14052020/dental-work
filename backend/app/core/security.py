from __future__ import annotations

import hashlib
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationError


# New hashes use pbkdf2_sha256 to avoid bcrypt backend incompatibilities in container builds.
# Existing bcrypt hashes remain verifiable for backward compatibility.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _encode_token(payload: dict[str, Any], *, expires_at: datetime) -> str:
    payload_with_exp = {**payload, "exp": expires_at}
    return jwt.encode(payload_with_exp, settings.secret_key, algorithm=ALGORITHM)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": subject, "type": "access", "jti": str(uuid4())}
    return _encode_token(payload, expires_at=expire)


def create_refresh_token(subject: str, expires_days: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=expires_days or settings.refresh_token_expire_days
    )
    payload: dict[str, Any] = {"sub": subject, "type": "refresh", "jti": str(uuid4())}
    return _encode_token(payload, expires_at=expire)


def decode_token(token: str, *, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AuthenticationError("Token is invalid or expired.") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise AuthenticationError("Token type is invalid.")

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Token subject is missing.")

    if expected_type == "refresh" and not payload.get("jti"):
        raise AuthenticationError("Refresh token identifier is missing.")

    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, expected_type="refresh")


def get_token_expiration(payload: dict[str, Any]) -> datetime:
    expires_at = payload.get("exp")
    if expires_at is None:
        raise AuthenticationError("Token expiration is missing.")

    if isinstance(expires_at, (int, float)):
        return datetime.fromtimestamp(expires_at, tz=timezone.utc)

    if isinstance(expires_at, datetime):
        return expires_at.astimezone(timezone.utc)

    raise AuthenticationError("Token expiration is invalid.")


def verify_token_hash(token: str, token_hash: str) -> bool:
    return hash_token(token) == token_hash
