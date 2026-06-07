from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, auth_get_current_user
from app.services.auth_services import AuthService
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import RefreshTokenSchema, LogoutSchema, PasswordResetConfirmSchema, PasswordResetRequestSchema, VerifyEmailSchema
from app.core.rate_limiter import limiter


auth_router = APIRouter()

@auth_router.post("/register")
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.register_user(db, data)

@auth_router.post("/verify-email")
async def verify_user_email(
    data: VerifyEmailSchema,
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.verify_email(db, data)

@auth_router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.login(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
#GET Current user
@auth_router.post("/me")
async def get_current_user(
    current_user = Depends(auth_get_current_user)
):
    return UserResponse.model_validate(current_user)

@auth_router.post("/refresh")
async def refresh_token(
    data: RefreshTokenSchema,
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.refresh(
        db=db,
        refresh_token_str=data.refresh_token
    )

@auth_router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await AuthService.logout(db, current_user)

@auth_router.post("/logout-all")
async def logout_all(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await AuthService.logout_all(db, current_user)

@auth_router.post("/password-reset/request")
@limiter.limit("5/minute")
async def password_reset_request(
    request: Request,
    data: PasswordResetRequestSchema,
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.request_password_reset(db, data.email)

@auth_router.post("/password-reset/confirm")
async def password_reset_confirm(
    data: PasswordResetConfirmSchema,
    db: AsyncSession = Depends(get_async_db)
):
    return await AuthService.confirm_password_reset(
        db=db,
        email=data.email,
        code=data.code,
        new_password=data.new_password
    )