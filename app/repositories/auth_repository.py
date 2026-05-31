from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.auth_model import RefreshToken
from app.models.user_model import User
from datetime import datetime, timezone


class AuthRepository:
    @staticmethod
    async def create_refresh_token(db: AsyncSession, token: RefreshToken):
        db.add(token)
        await db.flush()
        return token

    @staticmethod
    async def get_refresh_token(db: AsyncSession, token_str: str):
        stmt = select(RefreshToken).where(RefreshToken.token == token_str)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    @staticmethod
    async def revoke_token(db: AsyncSession, token: RefreshToken):
        token.is_revoked = True
        await db.flush()
        return token
    
    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: UUID):
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await db.execute(stmt)
        tokens = result.scalars().all()

        for t in tokens:
            t.is_revoked = True
        await db.flush()
        return tokens

    @staticmethod
    async def delete_expired_tokens(db: AsyncSession):
        stmt = select(RefreshToken).where(RefreshToken.expires_at < func.now())
        result = await db.execute(stmt)
        tokens = result.scalars().all()
        for t in tokens:
            await db.delete(t)
        await db.flush()
        return tokens

    @staticmethod
    async def set_reset_code(
        db: AsyncSession,
        user: User,
        code: str,
        expiry
    ):
        user.reset_token = code
        user.reset_token_expiry = expiry
        await db.flush()
        return user

    @staticmethod
    async def clear_reset_code(db: AsyncSession, user: User):
        user.reset_token = None
        user.reset_token_expiry = None
        await db.flush()
        return user
