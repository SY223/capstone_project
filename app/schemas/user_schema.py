from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    pass

    @field_validator("name") 
    def normalize_name(cls, value): 
        return value.strip().lower() 
        
    @field_validator("email") 
    def normalize_email(cls, value): 
        return value.strip().lower()

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None 
    email: Optional[EmailStr] = None 
    role: Optional[UserRole] = None

    @field_validator("name") 
    def normalize_name(cls, value): 
        return value.strip().lower() 
        
    @field_validator("email") 
    def normalize_email(cls, value): 
        return value.strip().lower()


