from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user_schema import UserResponse
from app.schemas.course_schema import CourseResponse
from uuid import UUID
from datetime import datetime

class EnrollmentBase(BaseModel):
    user_id: UUID
    course_id: UUID

class EnrollmentCreate(BaseModel):
    course_id: UUID

class EnrollmentResponse(EnrollmentBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EnrollmentUpdate(BaseModel):
    user_id: Optional[UUID] = None
    course_id: Optional[UUID] = None

class EnrollmentDetails(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    code: str
    enrolled_on: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EnrollmentAdminDetails(BaseModel):
    id: UUID
    student_id: UUID
    student_email: str
    course_id: UUID
    course_title: str
    course_code: str
    enrolled_on: datetime

    model_config = ConfigDict(from_attributes=True)

class TeacherCourseEnrollmentSummary(BaseModel):
    course_id: UUID
    title: str
    code: str
    capacity_left: int
    total_enrolled: int
    enrolled_on: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedAdminEnrollmentResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[EnrollmentAdminDetails]
    
class PaginatedStudentEnrollmentResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[EnrollmentDetails]
