from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_async_db, auth_get_current_user
from app.schemas.user_schema import UserResponse, UserUpdate, PaginatedUserResponse
from app.services.user_services import UserService
from app.core.rate_limiter import limiter

user_router = APIRouter()


#ADMIN GET ALL ACTIVE
@user_router.get("/active", response_model=PaginatedUserResponse)
@limiter.limit("30/minute")
async def list_all_active_users(
    request: Request,
    page: int = 1, 
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.admin_list_all_active_users(db, current_user, page, limit)

#ADMIN GET ALL INACTIVE USERS
@user_router.get("/inactive", response_model=PaginatedUserResponse)
@limiter.limit("30/minute")
async def list_all_inactive_users(
    request: Request,
    page: int = 1, 
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.admin_list_all_inactive_users(db, current_user, page, limit)

#ADMIN GET A USER BY ID
@user_router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("30/minute")
async def get_user_by_id(
    request: Request,
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.get_user_by_id(db, user_id, current_user)

#PUT: ADMIN FULLY UPDATE A USER
@user_router.put("/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user(
    request: Request,
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.update_user(db, user_id, data, current_user)

#PATCH: ADMIN PARTIAL USER UPDATE
@user_router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
async def partial_update_user(
    request: Request,
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.update_user(db, user_id, data, current_user)

#ADMIN DELETE A USER
@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    await UserService.delete_user(db, user_id, current_user)

    

    
