
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from uuid import UUID
from app.core.cache import cache_get, cache_set, cache_delete_pattern
from app.repositories.course_repository import CourseRepository
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseResponse, CoursePut, CoursePatch
from app.schemas.pagination import PaginatedResult
from app.core.enums import UserRole

class CourseService:
    @staticmethod
    async def create_course(
        db: AsyncSession,
        data: CourseCreate,
        current_user
    ):
        if current_user.role != UserRole.teacher:
            raise HTTPException(status_code=403, detail="Only teachers can create courses")
        existing = await CourseRepository.get_course_by_code(db, data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists"
            )
        course_dict = {
            "title": data.title,
            "code": data.code,
            "capacity": 40,
            "is_active": True,
            "owner_id": current_user.id
        }
        course = await CourseRepository.create(db, course_dict)
        await db.commit()
        await db.refresh(course)
        await cache_delete_pattern("courses:*")
        return CourseResponse.model_validate(course)

    @staticmethod
    async def get_course_by_id(
        db: AsyncSession,
        course_id: UUID
    ):
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        return CourseResponse.model_validate(course)

    @staticmethod
    async def public_list_all_courses(
        db: AsyncSession,
        page: int = 0, 
        limit: int = 20
    ):
        cache_key = f"courses:{page}:{limit}"
        cached = await cache_get(cache_key)
        if cached:
            return PaginatedResult[CourseResponse](
                total=cached["total"],
                skip=cached["page"],
                limit=cached["limit"],
                items=[CourseResponse(**item) for item in cached["items"]]
            )
        courses = await CourseRepository.list_all(db, page, limit)
        if courses["total"] == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active courses in database")
        items = [
            CourseResponse.model_validate(c).model_dump(mode="json")
            for c in courses["items"]
        ]
        result_dict = {
            "total": courses["total"],
            "page": page,
            "limit": limit,
            "items": items
        }
        await cache_set(cache_key, result_dict, ttl=300)
        return PaginatedResult[CourseResponse](
            total=courses["total"],
            skip=page,
            limit=limit,
            items=[CourseResponse(**item) for item in items]
        )
        
    
    @staticmethod
    async def admin_list_all_courses(
        db: AsyncSession,
        current_user,
        page: int = 0,
        limit: int = 20
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can view all courses"
            )
        courses = await CourseRepository.list_all_admin(db, page, limit)
        if courses["total"] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No courses found"
            )
        return PaginatedResult[CourseResponse](
            total=courses["total"],
            skip=page,
            limit=limit,
            items=[CourseResponse.model_validate(c) for c in courses["items"]]
        )
    
    @staticmethod
    async def update_course(
        db: AsyncSession,
        course_id: UUID,
        data: CourseUpdate | CoursePut | CoursePatch,
        current_user
    ):
        if current_user.role != UserRole.teacher:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only teachers can update courses"
        )
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if course.owner_id != current_user.id:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not the owner of this course"
        )
        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update inactive course"
            )
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            existing = await CourseRepository.get_course_by_code(db, update_data["code"])
            if existing and existing.id != course.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")
        for key, value in update_data.items():
            setattr(course, key, value)
        await db.commit()
        await db.refresh(course)
        return CourseResponse.model_validate(course)
        

    @staticmethod
    async def delete_course(
        db: AsyncSession,
        course_id: UUID,
        current_user
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not allowed to delete this course"
        )
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        await CourseRepository.delete_course(db, course)
        await db.commit()
        return {
            "message": "Course deleted successfully"
        }

    @staticmethod
    async def deactivate_course(
        db: AsyncSession,
        course_id: UUID,
        current_user
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can deactivate courses"
            )
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if not course.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is already inactive")
        await CourseRepository.set_active_status(db, course, False)
        await db.commit()
        await db.refresh(course)

        return {
            "message": "Course deactivated successfully."
        }

    @staticmethod
    async def reactivate_course(
        db: AsyncSession,
        course_id: UUID,
        current_user
    ):
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can reactivate courses"
            )
        course = await CourseRepository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if course.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is already active")
        await CourseRepository.set_active_status(db, course, True)
        await db.commit()
        await db.refresh(course)

        return {
            "message": "Course reactivated successfully."
        }




