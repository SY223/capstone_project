from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
import re

class CourseBase(BaseModel):
    title: str
    code: str

    @field_validator("code") 
    def validate_course_code(cls, value):
        if not value or not value.strip(): 
            return value
        pattern = r"^[A-Za-z]{3}\d{3}$"
        if not re.match(pattern, value): 
            raise ValueError("Course code not right") 
        return value.upper()
    
    @field_validator("title") 
    def normalize_title(cls, value): 
        return value.strip().lower()

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: UUID
    owner_id: UUID
    capacity: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class CoursePut(BaseModel):
    title: str
    code: str

class CoursePatch(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
    owner_id: Optional[UUID] = None

    @field_validator("title") 
    def normalize_title(cls, value): 
        return value.strip().lower()