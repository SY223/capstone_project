from uuid import UUID, uuid4 
from datetime import datetime 
from app.schemas.user_schema import UserResponse, UserUpdate, UserCreate
from app.core.db import users_db


class UserService:
    @staticmethod
    def create_user(user_create: UserCreate):
        if not user_create.name or not user_create.name.strip():  # type: ignore
            raise ValueError("Name is required") 
        if not user_create.email:  # type: ignore
            raise ValueError("Email is required")
        if not user_create.role or not user_create.role.strip():
            raise ValueError("role cannot be empty")
        if user_create.role not in ("student", "admin"):  # type: ignore
            raise ValueError("Invalid role")
        for u in users_db.values():
            if u.email.lower() == user_create.email.lower():
                raise ValueError("A user with this email already exist")
        user = UserResponse(
            id=uuid4(), # type: ignore
            name=user_create.name, # type: ignore
            email=user_create.email,
            role=user_create.role,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        users_db[user.id] = user
        return user

    @staticmethod
    def get_user_by_id(user_id: UUID):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    @staticmethod
    def get_all_users():
        users = list(users_db.values())
        if not users:
            raise ValueError("No users found")
        return users

    @staticmethod
    def update_user(user_id: UUID, data: UserUpdate):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User not found")
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.role is not None:
            user.role = data.role
        user.updated_at = datetime.utcnow()
        users_db[user_id] = user
        return user

    @staticmethod
    def delete_user(user_id: UUID):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User not found.")
        del users_db[user_id]



