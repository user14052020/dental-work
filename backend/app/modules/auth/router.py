from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_auth_service, get_current_user
from app.modules.auth.schemas import (
    AuthTokenRead,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserRead,
)
from app.modules.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthTokenRead, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> AuthTokenRead:
    return await service.register(payload)


@router.post("/login", response_model=AuthTokenRead)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> AuthTokenRead:
    return await service.login(payload)


@router.post("/refresh", response_model=AuthTokenRead)
async def refresh(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthTokenRead:
    return await service.refresh(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> Response:
    await service.logout(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
async def me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
