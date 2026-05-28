from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_async_db
from app.schemas.pagination import PaginatedResult
from app.services.course_services import CourseService
from app.schemas.course_schema import CourseCreate, CoursePut, CoursePatch, CourseResponse
from app.core.deps import auth_get_current_user


course_router = APIRouter()

# Teacher create courses
@course_router.post("/")
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.create_course(db, data, current_user)

# Teacher, Admin, Student Retrieve all active courses
@course_router.get("/", response_model=PaginatedResult[CourseResponse])
async def list_courses(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.list_all_courses(db, current_user)

#Admin retrieve all courses with inactive courses
@course_router.get("/admin/all", response_model=PaginatedResult[CourseResponse])
async def admin_list_all_courses(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.admin_list_all_courses(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit
    )

#Teacher fully replace active courses: PUT
@course_router.put("/{course_id}", response_model=CourseResponse)
async def replace_course(
    course_id: UUID,
    data: CoursePut,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.update_course(db, course_id, data, current_user)

    
# Teacher Partially update active courses: PATCH
@course_router.patch("/{course_id}", response_model=CourseResponse)
async def patch_course(
    course_id: UUID,
    data: CoursePatch,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.update_course(db, course_id, data, current_user)

#Admin delete course
@course_router.delete("/{course_id}")
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.delete_course(db, course_id, current_user)

#Admin deactivate course
@course_router.patch("/{course_id}/deactivate")
async def deactivate_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.deactivate_course(db, course_id, current_user)

#Admin Reactivate Course
@course_router.patch("/{course_id}/reactivate")
async def reactivate_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.reactivate_course(db, course_id, current_user)
