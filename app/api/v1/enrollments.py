from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import auth_get_current_user, get_async_db
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentAdminDetails, TeacherCourseEnrollmentSummary
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
@enrollment_router.get("/me")
async def get_my_enrollments(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.list_student_enrollments(db, current_user)

#ADMIN GET all enrollments
@enrollment_router.get("/admin/all", response_model=list[EnrollmentAdminDetails])
async def admin_get_all_enrollments(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.admin_list_all_enrollments(db, current_user)

#TEACHER GET all enrollments per course
@enrollment_router.get("/teacher/my-courses", response_model=list[TeacherCourseEnrollmentSummary])
async def teacher_get_course_enrollments(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.teacher_list_course_enrollments(db, current_user)

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