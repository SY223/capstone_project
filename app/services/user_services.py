from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import  UserUpdate, UserCreate, UserResponse
from app.models.user_model import User, UserRole
from app.core.security import hash_password
from uuid import UUID



class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate):
        existing = await UserRepository.get_user_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
                # 2. Validate role
        if data.role not in UserRole:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Allowed roles: student, teacher, admin"
            )
        if len(data.hashed_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters long."
            )

        user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.hashed_password),
            role=data.role,
            is_active=True
        )
        try:
            user = await UserRepository.create_user(db, user)
            await db.commit()
            await db.refresh(user)
            return UserResponse.model_validate(user)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
        
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID):
        #UUID Validation
        if not isinstance(user_id, UUID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        return user
    
    @staticmethod
    async def list_all_users(db: AsyncSession):
        return await UserRepository.list_all_users(db)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate):
        user = await UserService.get_user_by_id(db, user_id)
        update_data = data.model_dump(exclude_unset=True)
        if "hashed_password" in update_data:
            update_data["hashed_password"] = hash_password(update_data["hashed_password"])
        try:
            user = await UserRepository.update_user(db, user, update_data)
            await db.commit()
            await db.refresh(user)
            return user
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
    async def delete_user(db: AsyncSession, user_id: UUID):
        user = await UserService.get_user_by_id(db, user_id)
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
            




