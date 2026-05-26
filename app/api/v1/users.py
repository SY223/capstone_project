from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_async_db
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_services import UserService  

user_router = APIRouter()

#Create a User
@user_router.post("/",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    return await UserService.create_user(db, data)

#Get a user by ID
@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    return await UserService.get_user_by_id(db, user_id)

#Get all Users
@user_router.get("/", response_model=list[UserResponse])
async def list_all_users(db: AsyncSession = Depends(get_async_db)):
    return await UserService.list_all_users(db)

#Fully update a user
@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    return await UserService.update_user(db, user_id, data)

#partial Update of user
@user_router.patch("/{user_id}", response_model=UserResponse)
async def partial_update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    return await UserService.update_user(db, user_id, data)

#Delete a User
@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    await UserService.delete_user(db, user_id)

    

    
