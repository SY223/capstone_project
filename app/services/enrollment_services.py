from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.course_repository import CourseRepository
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentResponse, EnrollmentDetails, EnrollmentAdminDetails, TeacherCourseEnrollmentSummary
from app.models.user_model import UserRole

class EnrollmentService:
    @staticmethod
    async def enroll_student(
        db: AsyncSession,
        data: EnrollmentCreate,
        current_user
    ):
        if current_user.role != UserRole.student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can enroll in courses"
            )
        user_id = current_user.id
        course_id = data.course_id
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot enroll in an inactive course"
            )
        if course.capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is full"
            )
        existing = await EnrollmentRepository.get_by_user_and_course(
            db, user_id, course_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already enrolled in this course"
            )
        enrollment_dict = {"user_id": user_id, "course_id": course_id}
        enrollment = await EnrollmentRepository.create_enrollment(db, enrollment_dict)
        course.capacity -= 1

        await db.commit()
        await db.refresh(enrollment)
        await db.refresh(course)

        return EnrollmentResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            created_at=enrollment.created_at
        )
    #Student List their enrolled courses
    @staticmethod
    async def list_student_enrollments(
        db: AsyncSession,
        current_user
    ):
        if current_user.role != UserRole.student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can view their enrollments"
            )
        enrollments = await EnrollmentRepository.list_by_user(db, current_user.id)
        if not enrollments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not enrolled in any courses"
            )
        return [
            EnrollmentDetails(
                id=e.id,
                course_id=e.course.id,
                title=e.course.title,
                code=e.course.code,
                enrolled_on=e.created_at
            )
            for e in enrollments
        ]
    #ADMIN list all enrollments
    @staticmethod
    async def admin_list_all_enrollments(
        db: AsyncSession,
        current_user
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can view all enrollments"
            )
        enrollments = await EnrollmentRepository.admin_list_all(db)
        if not enrollments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No enrollments found"
            )
        return [
            EnrollmentAdminDetails(
                id=e.id,
                student_id=e.student.id,
                student_email=e.student.email,
                course_id=e.course.id,
                course_title=e.course.title,
                course_code=e.course.code,
                enrolled_on=e.course.created_at
            )
            for e in enrollments
        ]


    #Teacher list all enrollments per course
    @staticmethod
    async def teacher_list_course_enrollments(
        db: AsyncSession,
        current_user
    ):
        if current_user.role != UserRole.teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can view enrollments on their courses"
            )
        courses = await CourseRepository.list_courses_with_enrollments_for_teacher(
            db, current_user.id
        )
        if not courses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You have not created any courses"
            )
        summaries = []
        for course in courses:
            total_enrolled = len(course.enrollments)
            capacity_left = course.capacity

            summaries.append(
                TeacherCourseEnrollmentSummary(
                    course_id=course.id,
                    title=course.title,
                    code=course.code,
                    total_enrolled=total_enrolled,
                    capacity_left=capacity_left
                )
            )
        return summaries

    #Student deregister from a course
    @staticmethod
    async def unenroll_student(
        db: AsyncSession,
        enrollment_id: UUID,
        current_user
    ):
        if current_user.role != UserRole.student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can unenroll from courses"
            )
        enrollment = await EnrollmentRepository.get_enrollment_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        if enrollment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot unenroll another user"
            )

        course = enrollment.course
        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unenroll from an inactive course"
            )
        await EnrollmentRepository.delete(db, enrollment)
        course.capacity += 1
        await db.commit()
        await db.refresh(course)
        return {
            "message": f"You have successfully deregister from {course.title.title()}"
        }