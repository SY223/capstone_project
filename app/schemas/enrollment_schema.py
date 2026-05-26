from typing import Optional
from pydantic import BaseModel
from app.schemas.user_schema import UserResponse
from app.schemas.course_schema import CourseResponse
from uuid import UUID
from datetime import datetime

class EnrollmentBase(BaseModel):
    user_id: UUID
    course_id: UUID

class EnrollmentCreate(EnrollmentBase):
    pass

# class EnrollmentRequest(BaseModel):
#     course_id: UUID

class EnrollmentResponse(EnrollmentBase):
    id: UUID
    created_at: datetime

class EnrollmentUpdate(BaseModel):
    user_id: Optional[UUID] = None
    course_id: Optional[UUID] = None

class EnrollmentDetails(BaseModel):
    id: UUID
    student: UserResponse
    course: CourseResponse
    enrolled_on: datetime

