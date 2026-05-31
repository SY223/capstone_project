from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_async_db, auth_get_current_user
from app.schemas.user_schema import UserResponse, UserUpdate
from app.services.user_services import UserService  

user_router = APIRouter()


#Get a user by ID
@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.get_user_by_id(db, user_id, current_user)

#Get all Users
@user_router.get("/", response_model=list[UserResponse])
async def list_all_users(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.list_all_users(db, current_user)

#Fully update a user
@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.update_user(db, user_id, data, current_user)

#partial Update of user
@user_router.patch("/{user_id}", response_model=UserResponse)
async def partial_update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    return await UserService.update_user(db, user_id, data, current_user)

#Delete a User
@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(auth_get_current_user)
):
    await UserService.delete_user(db, user_id, current_user)

    

    
