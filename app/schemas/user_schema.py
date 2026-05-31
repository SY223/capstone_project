from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Literal, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

    @field_validator("full_name") 
    def normalize_name(cls, value): 
        return value.strip().lower() 
        
    @field_validator("email") 
    def normalize_email(cls, value): 
        return value.strip().lower()

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
    
class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None 
    email: Optional[EmailStr] = None 
    role: Optional[UserRole] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("full_name") 
    def normalize_fullName(cls, value): 
        return value.strip().lower() 
        
    @field_validator("email") 
    def normalize_email(cls, value): 
        return value.strip().lower()


