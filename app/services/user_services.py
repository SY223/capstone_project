from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.user_model import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import  UserUpdate, UserRead
from app.core.cache import cache_delete_pattern, cache_get, cache_set
from app.core.security import hash_password
from uuid import UUID



class UserService:      
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID, current_user):
        if current_user.role != UserRole.admin:
            HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can perform this action"
            )
        #UUID Validation
        if not isinstance(user_id, UUID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        key = f"user:{user_id}"
        cached = await cache_get(key)
        if cached:
            return cached

        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        user_dict = UserRead.model_validate(user).model_dump(mode="json")
        await cache_set(key, user_dict, ttl=300)
        return user_dict
    
    @staticmethod
    async def list_all_users(db: AsyncSession, current_user):
        if current_user.role != UserRole.admin:
            HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can perform this action"
            )
        return await UserRepository.list_all_users(db)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate, current_user):
        if current_user.role != UserRole.admin:
            HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can update user"
            )
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        update_data = data.model_dump(exclude_unset=True)
        if "hashed_password" in update_data:
            update_data["hashed_password"] = hash_password(update_data["hashed_password"])
        try:
            user = await UserRepository.update_user(db, user, update_data)
            await db.commit()
            await db.refresh(user)
            await cache_delete_pattern(f"user:{user_id}")
            return UserRead.model_validate(user)
        except IntegrityError as e:
            await db.rollback()
            if "users_email_key" in str(e.orig) or "unique constraint" in str(e.orig).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid update operation"
            )
        
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID, current_user):
        if current_user.role != UserRole.admin:
            HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can perform this action"
            )
        user = await UserService.get_user_by_id(db, user_id, current_user)
        try:
            await UserRepository.delete_user(db, user)
            await db.commit()
            return {"message": "User deleted successfully"}
        except IntegrityError as e:
            await db.rollback()
            if "foreign key constraint" in str(e.orig).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User cannot be deleted because other records depend on it."
                )
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to delete user due to database constraints."
                )
            




