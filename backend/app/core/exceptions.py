from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any


@dataclass
class ServiceError(Exception):
    message: str
    code: str
    status_code: int = HTTPStatus.BAD_REQUEST
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, request_id: str | None = None) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }


class NotFoundError(ServiceError):
    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            message=f"{entity_name} was not found.",
            code=f"{entity_name.lower()}_not_found",
            status_code=HTTPStatus.NOT_FOUND,
            details={"id": identifier},
        )


class ConflictError(ServiceError):
    def __init__(self, message: str, *, code: str = "conflict", details: dict[str, Any] | None = None):
        super().__init__(message=message, code=code, status_code=HTTPStatus.CONFLICT, details=details or {})


class AuthenticationError(ServiceError):
    def __init__(self, message: str = "Invalid credentials."):
        super().__init__(message=message, code="authentication_failed", status_code=HTTPStatus.UNAUTHORIZED)


class AuthorizationError(ServiceError):
    def __init__(self, message: str = "You are not allowed to perform this action."):
        super().__init__(message=message, code="forbidden", status_code=HTTPStatus.FORBIDDEN)
