from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_async_db
from app.schemas.pagination import PaginatedResult
from app.services.course_services import CourseService
from app.schemas.course_schema import CourseCreate, CoursePut, CoursePatch, CourseResponse, CourseResponseUser
from app.core.deps import auth_get_current_user
from app.core.rate_limiter import limiter


course_router = APIRouter()

# Teacher create courses
@course_router.post("/")
@limiter.limit("10/minute")
async def create_course(
    request: Request,
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.create_course(db, data, current_user)

# Public Retrieve all active courses
@course_router.get("/", response_model=PaginatedResult[CourseResponse])
@limiter.limit("60/minute")
async def list_courses(
    request: Request,
    page: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db)
):
    return await CourseService.public_list_all_courses(db, page, limit)

#Admin retrieve all courses with inactive courses
@course_router.get("/admin/all", response_model=PaginatedResult[CourseResponse])
@limiter.limit("30/minute")
async def admin_list_all_courses(
    request: Request,
    page: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.admin_list_all_courses(db, current_user, page, limit)

#Teacher fully replace active courses: PUT
@course_router.put("/{course_id}", response_model=CourseResponse)
@limiter.limit("20/minute")
async def replace_course(
    request: Request,
    course_id: UUID,
    data: CoursePut,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.update_course(db, course_id, data, current_user)

    
# Teacher Partially update active courses: PATCH
@course_router.patch("/{course_id}", response_model=CourseResponse)
@limiter.limit("20/minute")
async def patch_course(
    request: Request,
    course_id: UUID,
    data: CoursePatch,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.update_course(db, course_id, data, current_user)

#Admin delete course
@course_router.delete("/{course_id}")
@limiter.limit("10/minute")
async def delete_course(
    request: Request,
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.delete_course(db, course_id, current_user)

#Admin deactivate course
@course_router.patch("/{course_id}/deactivate", response_model=CourseResponseUser)
@limiter.limit("10/minute")
async def deactivate_course(
    request: Request,
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.deactivate_course(db, course_id, current_user)

#Admin Reactivate Course
@course_router.patch("/{course_id}/reactivate", response_model=CourseResponseUser)
@limiter.limit("10/minute")
async def reactivate_course(
    request: Request,
    course_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await CourseService.reactivate_course(db, course_id, current_user)
