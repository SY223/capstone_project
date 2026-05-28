from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment

class EnrollmentRepository:
    @staticmethod
    async def create_enrollment(db: AsyncSession, data: dict):
        enrollment = Enrollment(**data)
        db.add(enrollment)
        await db.flush()
        return enrollment
    
    #GET an enrollment by its ID
    @staticmethod
    async def get_enrollment_by_id(
        db: AsyncSession,
        enrollment_id: UUID
    ):
        result = await db.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
        return result.scalar_one_or_none()

    #GET an enrollment by user_id and course_id
    @staticmethod
    async def get_by_user_and_course(
        db: AsyncSession,
        user_id: UUID,
        course_id: UUID
    ):
        result = await db.execute(
            select(Enrollment)
            .where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
        )
        return result.scalar_one_or_none()

    #List all enrollments of a user
    @staticmethod
    async def list_by_user(db: AsyncSession, user_id: UUID):
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .options(
                selectinload(Enrollment.course),
                selectinload(Enrollment.student)
            )
        )
        return result.scalars().all()

    #Admin GET all enrollments
    @staticmethod
    async def admin_list_all(db: AsyncSession):
        result = await db.execute(
            select(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.course)
            )
        )
        return result.scalars().all()



    #DELETE deregister a user enrollment
    @staticmethod
    async def delete(db: AsyncSession, enrollment: Enrollment):
        await db.delete(enrollment)
        await db.flush()

    