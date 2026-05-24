from fastapi import HTTPException, status, Header, Depends
from app.schemas.user_schema import UserRole, UserResponse
from app.services.user_services import UserService
from app.core.db import users_db, enrollments_db
from uuid import UUID


def get_current_user(x_user_id: UUID = Header(...)):
    try:
        user_id = x_user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def is_admin_user(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user

def is_student_user(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses"
        )
    return current_user
