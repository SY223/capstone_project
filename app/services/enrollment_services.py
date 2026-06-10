from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.course_repository import CourseRepository
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentResponse, EnrollmentDetails, EnrollmentAdminDetails, TeacherCourseEnrollmentSummary
from app.core.enums import UserRole

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
        current_user,
        page: int = 1,
        limit: int = 20
    ):
        if current_user.role != UserRole.student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can view their enrollments"
            )
        skip = (page-1) * limit
        enrollments = await EnrollmentRepository.list_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
        total = await EnrollmentRepository.count_by_user(db, current_user.id)
        if not enrollments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not enrolled in any courses"
            )
        items = [
            EnrollmentDetails(
                id=e.id,
                course_id=e.course.id,
                title=e.course.title,
                code=e.course.code,
                enrolled_on=e.created_at
            )
            for e in enrollments
        ]
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items
        }
    #ADMIN list all enrollments
    @staticmethod
    async def admin_list_all_enrollments(
        db: AsyncSession,
        current_user,
        page: int = 1,
        limit: int = 20
    ):
        
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can view all enrollments"
            )
        skip = (page-1) * limit
        enrollments = await EnrollmentRepository.admin_list_all(db, skip=skip, limit=limit)
        total = await EnrollmentRepository.admin_count_all(db)
        if not enrollments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No enrollments found"
            )
        items = [
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
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items
        }


    #TEACHER or ADMIN list all enrollments per course
    @staticmethod
    async def teacher_admin_list_course_enrollments(
        db: AsyncSession,
        current_user,
        course_id: UUID,
        page: int = 1,
        limit: int = 20
    ):
        if current_user.role not in [UserRole.teacher, UserRole.admin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view enrollments"
            )
        skip = (page-1) * limit
        course = None
        if current_user.role == UserRole.admin:
            course = await CourseRepository.get_course_with_enrollments_for_admin(
                db, course_id=course_id
            )
        elif current_user.role == UserRole.teacher:
            course = await CourseRepository.get_course_with_enrollments_for_teacher(
                db, course_id=course_id, teacher_id=current_user.id
            )
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found or you do not have permission to view it."
            )
        all_enrollments = course.enrollments
        total = len(all_enrollments)
        paginated_enrollments = all_enrollments[skip : skip + limit]
        
        items = [
            {
                "id": e.id,
                "student_id": e.student.id,
                "student_email": e.student.email,
                "course_id": course.id,
                "course_title": course.title,
                "course_code": course.code,
                "enrolled_on": e.created_at
            }
            for e in paginated_enrollments
        ]
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items
        }

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
    
    #ADMIN remove student from course
    @staticmethod
    async def admin_remove_student_from_course(
        db: AsyncSession,
        enrollment_id: UUID,
        current_user
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can remove student from a course"
            )
        enrollment = await EnrollmentRepository.get_enrollment_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        student_id = enrollment.user_id
        course_id = enrollment.course_id
        course = enrollment.course
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        await EnrollmentRepository.delete(db, enrollment)
        course.capacity += 1
        await db.commit()
        await db.refresh(course)

        return {
            "message": "Student removed successfully",
            "student_id": student_id,
            "course_id": course_id
        }