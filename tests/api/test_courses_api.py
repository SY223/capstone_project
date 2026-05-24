from fastapi.testclient import TestClient 
from uuid import uuid4 
from datetime import datetime, timezone 
from app.main import app 
from app.schemas.course_schema import CourseResponse 
from app.core.db import courses_db, users_db
from app.api.deps import is_admin_user
import pytest

client = TestClient(app)

# ✅ Automatically clear DB before each test
@pytest.fixture(autouse=True)
def clear_users_db():
    users_db.clear()
    courses_db.clear()

def test_admin_create_course_success():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin User",
            "email": "admin@gmail.com",
            "role": "admin"
        }    
    )
    admin_id = admin_response.json()["id"]
    response = client.post(
        "api/v1/courses",
        json={
            "code": "CSC101",
            "title": "Introduction to Computer Science"
        },
        headers={"X-User-Id": admin_id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "CSC101"
    assert data["title"] == "introduction to computer science"
    assert "id" in data

def test_student_cannot_create_course():
    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "Student Paul",
            "email": "student.paul@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC102",
            "title": "Data Structures"
        },
        headers={"X-User-Id": student_id}
    )
    assert response.status_code == 403

def test_create_course_missing_header():
    response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC103",
            "title": "Algorithms"
        }
    )
    assert response.status_code == 422

def test_user_get_all_courses():
    user_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin User",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = user_response.json()["id"]
    client.post(
        "/api/v1/courses/",
        json={"code": "CSC101", "title": "Intro to CS"},
        headers={"X-User-Id": admin_id}
    )

    client.post(
        "/api/v1/courses/",
        json={"code": "MTH101", "title": "Calculus I"},
        headers={"X-User-Id": admin_id}
    )
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_no_courses_available():
    response = client.get("/api/v1/courses")

    assert response.status_code == 404
    assert response.json()["detail"] == "No courses available"

def test_get_course_by_id():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin User",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]
    create_response = client.post(
        "api/v1/courses",
        json={
            "code": "CSC101",
            "title": "Introduction to Computer Science"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = create_response.json()["id"]
    locate_course = client.get(f"/api/v1/courses/{course_id}")

    assert locate_course.status_code == 200
    data = locate_course.json()
    assert data["id"] == course_id

def test_get_course_by_fake_id():
    fake_id = uuid4()

    response = client.get(f"/api/v1/courses/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

def test_admin_replace_course():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin Bruv",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]
    create_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "GST301",
            "title": "Fundamentals of Sleeping"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = create_response.json()["id"]
    #replace_course
    update_response = client.put(
        f"/api/v1/courses/{course_id}",
        json={
            "code": "SLT301",
            "title": "New Advanced Title"
        },
        headers={"X-User-Id": admin_id}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == course_id
    assert data["code"] == "SLT301"
    assert data["title"] == "New Advanced Title"

def test_student_cannot_replace_course():
    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]

    fake_course_id = "11111111-1111-1111-1111-111111111111"
    response = client.put(
        f"/api/v1/courses/{fake_course_id}",
        json={
            "code": "CSC999",
            "title": "New Advanced Title"
        },
        headers={"X-User-Id": student_id}
    )
    assert response.status_code == 403

def test_admin_patch_course():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin Bruv",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]
    create_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "GST301",
            "title": "Fundamentals of Sleeping"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = create_response.json()["id"]
    #replace_course
    update_response = client.patch(
        f"/api/v1/courses/{course_id}",
        json={
            "title": "Fundamentals of Driving"
        },
        headers={"X-User-Id": admin_id}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "fundamentals of driving"


def test_admin_delete_course_success():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]
    create_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC401",
            "title": "Advanced Programming"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = create_response.json()["id"]

    # Delete course
    delete_response = client.delete(
        f"/api/v1/courses/{course_id}",
        headers={"X-User-Id": admin_id}
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

