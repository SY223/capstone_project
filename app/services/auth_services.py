from sentry_sdk import capture_exception
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from datetime import datetime, timezone, timedelta
from app.core.email_utils import send_email_365_async, send_email_postmark_async
from app.core.deps import generate_verification_code
from app.tasks.email_tasks import send_password_reset_email_task, send_verification_email_task
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token
)
from app.models.user_model import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.models.auth_model import RefreshToken
from app.core.config import settings
from app.schemas.auth_schema import VerifyEmailSchema
from app.schemas.user_schema import UserCreate


class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, data: UserCreate):
        hashed_pw = hash_password(data.password)

        code = generate_verification_code()
        expires = datetime.utcnow() + timedelta(settings.RESET_CODE_EXPIRY_MINUTES)
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed_pw,
            role=data.role,
            is_verified=False,
            verification_code=code,
            verification_expires_at=expires
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )
        #Details that goes to client
        try:
            send_verification_email_task.delay(user.email, user.full_name, code)
        except Exception as e:
            capture_exception(e)
        return {
            "message": "Your email verification code sent"
        }

    @staticmethod
    async def verify_email(db: AsyncSession, data: VerifyEmailSchema):
        user = await UserRepository.get_user_by_email(db, data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        if user.verification_code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        if (user.verification_expires_at is None or user.verification_code is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code. Please request a new one."
            )
        if user.verification_expires_at < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired"
            )
        user.is_verified = True
        user.verification_code = None
        user.verification_expires_at = None
        await db.commit()
        await db.refresh(user)
        return {
            "message": "Email verified successfully"
        }



    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str
    ):
        user = await UserRepository.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password"
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified. Please verify your email to continue"
            )
        access_token = create_access_token(
            {"sub": str(user.id),"role": user.role}
        )
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        await AuthRepository.create_refresh_token(db, refresh_token)
        await db.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str
        }
    
    @staticmethod
    async def refresh(db: AsyncSession, refresh_token_str: str):
        token = await AuthRepository.get_refresh_token(db, refresh_token_str)
        if not token or token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token"
            )
        if token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        token.is_revoked = True
        new_refresh_token_str = create_refresh_token({"sub": str(token.user_id)})
        new_refresh_token = RefreshToken(
            token=new_refresh_token_str,
            user_id = token.user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        await AuthRepository.create_refresh_token(db, new_refresh_token)
        await db.commit()
        new_access_token = create_access_token({"sub": str(token.user_id)})
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token_str
        }

    @staticmethod
    async def logout(db: AsyncSession, current_user):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You need to login"
            )
        await AuthRepository.revoke_token(db, current_user.refresh_tokens)
        await db.commit()
        return {"message": "Logged out successfully"}


    @staticmethod
    async def logout_all(db: AsyncSession, current_user):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to perform this action"
            )
        await AuthRepository.revoke_all_user_tokens(db, current_user.id)
        await db.commit()
        return {
            "message": "Logged out from all devices"
        }
    
    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str):
        user = await UserRepository.get_user_by_email(db, email)
        if not user:
            return {
                "message": "If this email exists, a reset code has been sent."
            }
        code = generate_verification_code()
        expiry = datetime.now(timezone.utc) + timedelta(settings.RESET_CODE_EXPIRY_MINUTES)
        await AuthRepository.set_reset_code(db, user, code, expiry)
        await db.commit()
        #Details that goes to client
        try:
            send_password_reset_email_task.delay(user.email, user.full_name, code)
        except Exception as e:
            capture_exception(e)
        return {
            "message": "if this email exists, a reset code has been sent."
        }

    @staticmethod
    async def confirm_password_reset(db: AsyncSession, email: str, code: str, new_password: str):
        user = await UserRepository.get_user_by_email(db, email)
        if not user or not user.reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset code"
            )
        if user.reset_token != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset code"
            )
        now = datetime.now(timezone.utc)
        if not user.reset_token_expiry or user.reset_token_expiry < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset code expired"
        )
        if user.reset_token_expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset code expired"
            )
        user.hashed_password = hash_password(new_password)
        await AuthRepository.clear_reset_code(db, user)
        await db.commit()
        return {
            "message": "Password reset successfull"
        }
