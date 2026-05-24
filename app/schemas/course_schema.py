from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
import re

class CourseBase(BaseModel):
    code: str
    title: str

    @field_validator("code") 
    def validate_course_code(cls, value):
        if not value or not value.strip(): 
            return value
        pattern = r"^[A-Za-z]{3}\d{3}$"
        if not re.match(pattern, value): 
            raise ValueError("Course code not right") 
        return value.upper()

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator("title") 
    def normalize_name(cls, value): 
        return value.strip().lower()

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None

    @field_validator("title") 
    def normalize_name(cls, value): 
        return value.strip().lower()