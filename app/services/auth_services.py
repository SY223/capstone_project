from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from app.core.email_utils import send_email_365_async, send_email_postmark_async
import random
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token
)
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.models.auth_model import RefreshToken
from app.core.config import settings

class AuthService:
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
        access_token = create_access_token(
            {"sub": str(user.id),"role": user.role}
        )
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
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
    async def logout(db: AsyncSession, refresh_token_str: str):
        token = await AuthRepository.get_refresh_token(db, refresh_token_str)
        if token:
            await AuthRepository.revoke_token(db, token)
            await db.commit()

        return {
            "message": "Logged out successfully"
        }

    @staticmethod
    async def logout_all(db: AsyncSession, user_id):
        await AuthRepository.revoke_all_user_tokens(db, user_id)
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
        code = f"{random.randint(100000, 999999)}"
        expiry = datetime.now(timezone.utc) + timedelta(settings.RESET_CODE_EXPIRY_MINUTES)
        await AuthRepository.set_reset_code(db, user, code, expiry)
        await db.commit()
        #Details that goes to client
        subject = "Your Password Reset Code"
        body = (
            f"Hello {user.full_name},\n\n"
            f"Your password reset code is: {code}\n\n"
            f"This code will expire in 15 minutes.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"Regards,\nYour App Team"
        )
        # await send_email_postmark_async(user.email, subject, body)

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
            "message": "Password has been reset successfully"
        }
