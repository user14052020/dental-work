from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import EmailStr, Field, StringConstraints

from app.common.schemas import BaseSchema


OptionalSubjectString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]


class NaradDocumentEmailPayload(BaseSchema):
    kind: Literal["invoice", "act", "job-order"]
    recipient_email: Optional[EmailStr] = None
    subject: OptionalSubjectString = None


class ClientDocumentEmailPayload(BaseSchema):
    kind: Literal["invoice", "act"]
    recipient_email: Optional[EmailStr] = None
    subject: OptionalSubjectString = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class DocumentEmailRead(BaseSchema):
    kind: str
    recipient_email: EmailStr
    subject: str
