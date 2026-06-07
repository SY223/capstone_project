from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import auth_get_current_user, get_async_db
from app.schemas.enrollment_schema import EnrollmentCreate, TeacherCourseEnrollmentSummary, PaginatedAdminEnrollmentResponse, PaginatedStudentEnrollmentResponse
from app.services.enrollment_services import EnrollmentService


enrollment_router = APIRouter()

#STUDENT enroll on a course
@enrollment_router.post("/")
async def enroll_student(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.enroll_student(db, data, current_user)

#STUDENT GET their enrollment lists
@enrollment_router.get("/me", response_model=PaginatedStudentEnrollmentResponse)
async def get_my_enrollments(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.list_student_enrollments(db, current_user, page, limit)

#ADMIN GET all enrollments
@enrollment_router.get("/admin/all", response_model=PaginatedAdminEnrollmentResponse)
async def admin_get_all_enrollments(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.admin_list_all_enrollments(db, current_user, page, limit)

#TEACHER and ADMIN GET all enrollments per course
@enrollment_router.get("/{course_id}", response_model=PaginatedAdminEnrollmentResponse)
async def teacher_admin_get_course_enrollments(
    course_id: UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.teacher_admin_list_course_enrollments(db, current_user, course_id, page, limit)

#STUDENT deregister from a course
@enrollment_router.delete("/{enrollment_id}")
async def unenroll_student_from_course(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.unenroll_student(db,enrollment_id, current_user)

#ADMIN remove student from course
@enrollment_router.delete("/admin/remove/{enrollment_id}")
async def admin_remove_student_from_course(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.admin_remove_student_from_course(db, enrollment_id, current_user)