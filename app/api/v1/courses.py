from fastapi import APIRouter, HTTPException, Depends, status
from uuid import uuid4, UUID
from app.services.course_services import CourseService
from app.schemas.course_schema import CourseCreate, CourseUpdate
from app.api.deps import is_admin_user
from typing import List


course_router = APIRouter()

#Admin create courses
@course_router.post("/", status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    admin_user = Depends(is_admin_user)
):
    try:
        return CourseService.create_course(course_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

#Retrieve all courses
@course_router.get("/", status_code=status.HTTP_200_OK)
def get_all_courses():
    try:
        return CourseService.get_all_courses()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

#Retrieve a course by unique id
@course_router.get("/{course_id}", status_code=status.HTTP_200_OK)
def get_course(course_id: UUID):
    try:
        return CourseService.get_course(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

#Admin fully replace course: PUT
@course_router.put("/{course_id}", status_code=status.HTTP_200_OK)
def replace_course(
    course_id: UUID,
    course_update: CourseCreate,
    admin_user = Depends(is_admin_user)
):
    try:
        updated_course = CourseService.replace_course(course_id, course_update)
        return updated_course
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
    
#Admin Partially update course: PATCH
@course_router.patch("/{course_id}")
def partial_update_course(course_id: UUID, course_update: CourseUpdate, admin_user = Depends(is_admin_user)):
    try:
        return CourseService.partial_update_course(course_id, course_update)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

#Admin delete course
@course_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: UUID,
    admin_user = Depends(is_admin_user)
):
    try:
        CourseService.delete_course(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
