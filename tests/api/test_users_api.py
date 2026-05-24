from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.core.db import users_db
from datetime import datetime, timezone
from uuid import uuid4
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_users_db():
    users_db.clear()

def test_create_user_endpoint():
    response = client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "john@gmail.com",
            "role": "student"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "john doe"
    assert data["email"] == "john@gmail.com"
    assert data["role"] == "student"

def test_get_user_by_id():
    response = client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "john@gmail.com",
            "role": "student"
        }
    )
    assert response.status_code == 201
    created_user = response.json()
    user_id = created_user["id"]

    response_get = client.get(f"/api/v1/users/{user_id}")
    assert response_get.status_code == 200
    data = response_get.json()

    assert data["id"] == user_id
    assert data["name"] == created_user["name"]
    assert data["email"] == created_user["email"]
    assert data["role"] == created_user["role"]


def test_update_user():
    created_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "john@gmail.com",
            "role": "student"
        }
    )
    assert created_response.status_code == 201
    user_id = created_response.json()["id"]
    update_response = client.put(
        f"/api/v1/users/{user_id}",
        json={
            "name": "Millie Cyprus",
            "email": "millie.cyprus@aol.com",
            "role": "admin"
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == user_id
    assert data["name"] == "millie cyprus"
    assert data["email"] == "millie.cyprus@aol.com"
    assert data["role"] == "admin"


def test_delete_user_success():  
    user_id = uuid4() 
    user = UserResponse( 
        id=user_id, 
        name="John Doe", 
        email="john@example.com", 
        role="student", 
        created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc) 
    ) 
    users_db[user_id] = user 
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert user_id not in users_db

def test_delete_user_not_found():  
    non_existent_id = uuid4()
    response = client.delete(f"/users/{non_existent_id}") 
    assert response.status_code == 404 
    assert response.json()["detail"] == "Not Found"