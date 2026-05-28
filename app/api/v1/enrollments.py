from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import auth_get_current_user, get_async_db
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentAdminDetails, TeacherCourseEnrollmentSummary
from app.services.enrollment_services import EnrollmentService


enrollment_router = APIRouter()

@enrollment_router.post("/")
async def enroll_student(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await EnrollmentService.enroll_student(db, data, current_user)

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





# #Admin retrieve course enrollments
# @enrollment_router.get("/admin/{course_id}/enrollments", response_model=List[EnrollmentDetails], status_code=status.HTTP_200_OK)
# def admin_retrieve_course_enrollments(
#     course_id: UUID,
#     admin_id: UUID = Depends(is_admin_user)
#     ):
#     try:
#         return EnrollmentService.admin_retrieve_course_enrollments(course_id)
#     except Exception as exc:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

# #Admin remove enrollments
# @enrollment_router.delete("/admin/force-deregister")
# def admin_force_deregister(
#     user_id: UUID,
#     course_id: UUID,
#     admin_id: UUID = Depends(is_admin_user)
#     ):
#     try:
#         return EnrollmentService.admin_force_deregister(user_id, course_id)
#     except Exception as exc:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))