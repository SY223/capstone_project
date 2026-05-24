from app.services.user_services import UserService
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.core.db import users_db
from uuid import uuid4
from datetime import datetime, timezone
import pytest



# ✅ Automatically clear DB before each test
@pytest.fixture(autouse=True)
def clear_users_db():
    users_db.clear()

def test_create_user():
    user = UserService.create_user(
        UserCreate(
            name="Bailey Paul",
            email="baileypaul@gmail.com",
            role="student"
        )
    )
    assert user.name == "bailey paul"
    assert user.email == "baileypaul@gmail.com"
    assert user.role == "student"
    assert user.id is not None


def test_get_all_users_success():
    user1 = UserService.create_user(
        UserCreate(
            name="John Doe",
            email="john@gmail.com",
            role="student"
        )
    )
    user2 = UserService.create_user(
        UserCreate(
            name="Jane Smith",
            email="jane@gmail.com",
            role="admin"
        )
    )
    users = UserService.get_all_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users
    assert user1.email == "john@gmail.com"
    assert user2.email == "jane@gmail.com"


def test_update_user_success(): 
    user_id = uuid4() 
    created_user = UserResponse(
        id=user_id, 
        name="John Doe", 
        email="john@example.com", 
        role="student", 
        created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc)
    ) 
    users_db[user_id] = created_user
    update_data = UserUpdate(
        name="Jane Doe", 
        email="jane@example.com", 
        role="admin",
        updated_at=datetime.now(timezone.utc)
    ) 
    updated_user = UserService.update_user(user_id, update_data)
    assert updated_user.name == "jane doe"
    assert updated_user.email == "jane@example.com"
    assert updated_user.role == "admin"
    assert updated_user.created_at != updated_user.updated_at

def test_delete_user_success():
    user_id = uuid4() 
    created_user = UserResponse(
        id=user_id, 
        name="John Doe", 
        email="john@example.com", 
        role="student", 
        created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc)
    )
    users_db[user_id] = created_user
    UserService.delete_user(user_id)
    assert user_id not in users_db

def test_delete_user_not_found():
    non_existent_id = uuid4() 
    with pytest.raises(ValueError) as exc: 
        UserService.delete_user(non_existent_id) 
    assert str(exc.value) == "User not found."