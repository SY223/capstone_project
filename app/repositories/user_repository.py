from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_model import User
from uuid import UUID

class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user: User):
        db.add(user)
        await db.flush()
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def list_all_users(db:AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def delete_user(db: AsyncSession, user: User):
        await db.delete(user)

    @staticmethod
    async def update_user(db: AsyncSession, user: User, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        await db.flush()
        return user