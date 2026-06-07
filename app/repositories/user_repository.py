from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
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
        if isinstance(user_id, str):
            user_id = UUID(user_id) 
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


    @staticmethod
    async def list_active_users_paginated(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20
    ):
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def list_inactive_users_paginated(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20
    ):
        result = await db.execute(
            select(User)
            .where(User.is_active == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def count_active_users(db: AsyncSession):
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar() or 0

    @staticmethod
    async def count_inactive_users(db: AsyncSession):
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == False)
        )
        return result.scalar() or 0
    
    
    @staticmethod
    async def delete_user(db: AsyncSession, user: User):
        await db.delete(user)

    @staticmethod
    async def update_user(db: AsyncSession, user: User, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        await db.flush()
        return user