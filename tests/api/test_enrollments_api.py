from fastapi.testclient import TestClient 
from uuid import uuid4, UUID
from datetime import datetime, timezone 
from app.main import app 
from app.schemas.course_schema import CourseResponse 
from app.core.db import courses_db, users_db, enrollments_db
from app.api.deps import is_admin_user
import pytest

client = TestClient(app)

#Clear DB before test starts
@pytest.fixture(autouse=True)
def clear_users_db():
    users_db.clear()
    courses_db.clear()
    enrollments_db.clear()

def test_student_enroll_success():
    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]
    # Create course
    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]
    # Enroll student
    enroll_response = client.post(
        "/api/v1/enrollments/",
        json={
            "course_id": course_id
        },
        headers={"X-User-Id": student_id}
    )
    assert enroll_response.status_code == 201
    data = enroll_response.json()
    print(data)
    assert data["user_id"] == student_id

"""Next Test"""

def test_student_retrieve_enrollments():
    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]

    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]

    enroll_response = client.post(
        "/api/v1/enrollments/",
        json={
            "course_id": course_id
        },
        headers={"X-User-Id": student_id}
    )
    enrollment_id = enroll_response.json()["id"]
    get_enrollment_response = client.get(
        f"/api/v1/enrollments/student/{student_id}/courses",
        headers={"X-User-Id": student_id}
    )
    assert get_enrollment_response.status_code == 200
    data = get_enrollment_response.json()
    assert data[0]["id"] == enrollment_id
    assert len(data) == 1
    assert isinstance(data, list)

"""Next Test"""
def test_student_deregister_enrollment(): 
    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]

    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]

    enroll_response = client.post(
        "/api/v1/enrollments/",
        json={
            "course_id": course_id
        },
        headers={"X-User-Id": student_id}
    )
    enrollment_id = enroll_response.json()["id"]
    assert enroll_response.status_code == 201

    deregister_response = client.delete(
        "/api/v1/enrollments",
        params={
            "user_id": student_id,
            "course_id": course_id
        }
    )
    assert deregister_response.status_code == 200
    data = deregister_response.json()
    assert data["message"] == "Successfully deregister from the course."

def test_admin_retrieve_enrollments():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]

    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]
    enroll_response = client.post(
        "/api/v1/enrollments/", 
        json={"course_id": course_id}, 
        headers={"X-User-Id": student_id} 
    )
    
    student_attempt = client.get(
        "/api/v1/enrollments/admin/enrollments", 
        headers={"X-User-Id": student_id} 
    )

    admin_attempt = client.get(
        "/api/v1/enrollments/admin/enrollments", 
        headers={"X-User-Id": admin_id} 
    )

    assert enroll_response.status_code == 201
    assert student_attempt.status_code == 403
    assert admin_attempt.status_code == 200
    data = enroll_response.json()
    assert data["course_id"] == course_id
    assert data["user_id"] == student_id

"""Next"""
def test_admin_retrieve_course_enrollments():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]

    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]
    enroll_response = client.post(
        "/api/v1/enrollments/", 
        json={"course_id": course_id}, 
        headers={"X-User-Id": student_id} 
    )
    student_attempt = client.get(
        f"/api/v1/enrollments/admin/{course_id}/enrollments",
        params={"course_id": course_id},
        headers={"X-User-Id": student_id} 
    )

    admin_attempt = client.get(
       f"/api/v1/enrollments/admin/{course_id}/enrollments",
       params={"course_id": course_id},
       headers={"X-User-Id": admin_id}
    )
    assert enroll_response.status_code == 201
    assert student_attempt.status_code == 403
    assert admin_attempt.status_code == 200
    data = admin_attempt.json() 
    assert isinstance(data, list)

"""Admin Force Deregister"""
def test_admin_deregister_student():
    admin_response = client.post(
        "/api/v1/users",
        json={
            "name": "Admin",
            "email": "admin@gmail.com",
            "role": "admin"
        }
    )
    admin_id = admin_response.json()["id"]

    student_response = client.post(
        "/api/v1/users",
        json={
            "name": "John Student",
            "email": "student@gmail.com",
            "role": "student"
        }
    )
    student_id = student_response.json()["id"]
    course_response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CSC500",
            "title": "Software Engineering"
        },
        headers={"X-User-Id": admin_id}
    )
    course_id = course_response.json()["id"]
    enroll_response = client.post(
        "/api/v1/enrollments/", 
        json={"course_id": course_id}, 
        headers={"X-User-Id": student_id} 
    )
    student_attempt = client.delete(
        f"/api/v1/enrollments/admin/force-deregister",
        params={"user_id": student_id, "course_id": course_id}, 
        headers={"X-User-Id": student_id} 
    )

    admin_attempt = client.delete(
       f"/api/v1/enrollments/admin/force-deregister",
       params={"user_id": student_id, "course_id": course_id},
        headers={"X-User-Id": admin_id}
    )
    assert enroll_response.status_code == 201
    assert student_attempt.status_code == 403
    assert admin_attempt.status_code == 200
