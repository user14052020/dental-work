from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing import Annotated

from app.common.schemas import TimestampedReadSchema


PasswordString = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: PasswordString


class LoginRequest(BaseModel):
    email: EmailStr
    password: PasswordString


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken", min_length=32, max_length=2048)


class UserRead(TimestampedReadSchema):
    email: EmailStr
    is_active: bool


class AuthTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    user: UserRead
