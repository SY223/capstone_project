from fastapi import APIRouter, HTTPException, Depends, status
from app.services.user_services import UserService
from app.schemas.user_schema import UserResponse, UserUpdate, UserCreate
from typing import List
from uuid import UUID


user_router = APIRouter()

#Create a User
@user_router.post("/",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    try:
        created_user = UserService.create_user(user_data)
        return created_user
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

#Get a user by ID
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: UUID):
    try:
        return UserService.get_user_by_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

#Get all Users
@user_router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users():
    try:
        return UserService.get_all_users()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

#update fully and partially a user: PUT
@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, payload: UserUpdate):
    try:
        return UserService.update_user(user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

#partial Update of user
@user_router.patch("/{user_id}")
def partial_update_user(user_id: UUID, user_update: UserUpdate):
    try:
        return UserService.update_user(user_id, user_update)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

#Delete a User
@user_router.delete("/{user_id}")
def delete_user(user_id: UUID):
    try:
        return UserService.delete_user(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

    
