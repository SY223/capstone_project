from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List
from app.services.enrollment_services import EnrollmentService
from app.schemas.enrollment_schema import EnrollmentResponse, EnrollmentRequest, EnrollmentDetails
from app.api.deps import is_admin_user, is_student_user
from uuid import UUID


enrollment_router = APIRouter()

@enrollment_router.post("/", status_code=status.HTTP_201_CREATED)
def enroll_student(
    learner_data: EnrollmentRequest,
    current_student = Depends(is_student_user)
):
    try:
        return EnrollmentService.enroll_student(
            user_id=current_student.id, 
            course_id=learner_data.course_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@enrollment_router.get("/student/{user_id}/courses")
def student_retrieve_enrollment(
        user_id: UUID,
        current_student = Depends(is_student_user)
    ):
    if current_student.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    enrollments = EnrollmentService.retrieve_student_enrollments(user_id)
    return enrollments


@enrollment_router.delete("/", status_code=status.HTTP_200_OK)
def student_deregister(
        user_id: UUID, 
        course_id: UUID
    ):
    """Student cancel their own enrollment"""
    try:
        return EnrollmentService.student_deregister(user_id, course_id)
    except ValueError as exc:
        if "not found" in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))



#ADMIN ENDPOINTS
#Admin retrieve enrollments
@enrollment_router.get("/admin/enrollments")
def admin_retrieve_enrollments(admin_id: UUID = Depends(is_admin_user)):
    try:
        return EnrollmentService.admin_retrieve_enrollments()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

#Admin retrieve course enrollments
@enrollment_router.get("/admin/{course_id}/enrollments", response_model=List[EnrollmentDetails], status_code=status.HTTP_200_OK)
def admin_retrieve_course_enrollments(
    course_id: UUID,
    admin_id: UUID = Depends(is_admin_user)
    ):
    try:
        return EnrollmentService.admin_retrieve_course_enrollments(course_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

#Admin remove enrollments
@enrollment_router.delete("/admin/force-deregister")
def admin_force_deregister(
    user_id: UUID,
    course_id: UUID,
    admin_id: UUID = Depends(is_admin_user)
    ):
    try:
        return EnrollmentService.admin_force_deregister(user_id, course_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))