from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.course_model import Course
from uuid import UUID

from app.models.enrollment_model import Enrollment


class CourseRepository:
    @staticmethod
    async def create(db: AsyncSession, data: dict):
        course = Course(**data)
        db.add(course)
        await db.flush()
        return course

    @staticmethod
    async def get_course_by_id(db: AsyncSession, course_id: UUID):
        result = await db.execute(select(Course).where(Course.id == course_id))
        return result.scalars().first()

    @staticmethod
    async def get_course_by_code(db: AsyncSession, code: str):
        result = await db.execute(select(Course).where(Course.code == code))
        return result.scalars().first()

    @staticmethod
    async def list_all(
        db: AsyncSession,
        skip: int = 0, 
        limit: int = 10
    ):
        total_result = await db.execute(select(func.count(Course.id)).where(Course.is_active == True))
        total = total_result.scalar_one()
        result = await db.execute(
            select(Course)
            .where(Course.is_active == True)
            .options(
                selectinload(Course.owner),
                selectinload(Course.students)
            )
            .offset(skip)
            .limit(limit)
        )
        items = result.scalars().all()
        return {
            "total": total,
            "items": items
        }
    
    @staticmethod
    async def list_all_admin(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ):
        total_result = await db.execute(select(func.count(Course.id)))
        total = total_result.scalar_one()

        result = await db.execute(
            select(Course)
            .options(
                selectinload(Course.owner),
                selectinload(Course.students)
            )
            .offset(skip)
            .limit(limit)
        )
        items = result.scalars().all()
        return {
            "total": total,
            "items": items
        }


    #TEACHER GET a course enrollments
    @staticmethod
    async def list_courses_with_enrollments_for_teacher(
        db: AsyncSession,
        teacher_id: UUID
    ):
        result = await db.execute(
            select(Course)
            .where(Course.owner_id == teacher_id)
            .options(
                selectinload(Course.enrollments).selectinload(Enrollment.student)
            )
        )
        return result.scalars().all()

    
    @staticmethod
    async def update_course(
        db: AsyncSession,
        course: Course,
        data: dict
    ):
        for field, value in data.items():
            setattr(course, field, value)
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def delete_course(db: AsyncSession, course: Course):
        await db.delete(course)
    
    @staticmethod
    async def set_active_status(
        db: AsyncSession,
        course: Course,
        is_active: bool
    ):
        course.is_active = is_active
        await db.flush()
        return course


