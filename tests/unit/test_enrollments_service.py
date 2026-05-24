from fastapi.testclient import TestClient 
from uuid import uuid4, UUID
from datetime import datetime, timezone 
from app.main import app
from app.schemas.course_schema import CourseResponse
from app.schemas.user_schema import UserResponse
from app.services.enrollment_services import EnrollmentService
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

def test_enroll_student():
    user_id = uuid4() 
    course_id = uuid4()

    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)

    assert enrollment.user_id == user_id
    assert enrollment.course_id == course_id
    assert enrollment.id in enrollments_db

def test_retrieve_student_enrollments():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)

    results = EnrollmentService.retrieve_student_enrollments(user_id)
    assert results[0].user_id == user_id 
    assert results[0].course_id == course_id

def test_student_has_no_enrollment():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    try:
        results = EnrollmentService.retrieve_student_enrollments(user_id)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No enrollments found." in str(exc)

def test_student_deregister_course():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)
    assert enrollment.id in enrollments_db

    result = EnrollmentService.student_deregister(user_id, course_id)
    assert enrollment.id not in enrollments_db


def test_admin_retrieve_enrollments():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)
    results = EnrollmentService.admin_retrieve_enrollments()
    assert len(results) == 1
    assert results[0].id == enrollment.id

def test_admin_retrieve_course_enrollments():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)
    results = EnrollmentService.admin_retrieve_course_enrollments(course_id)
    assert len(results) == 1
    assert results[0].id == enrollment.id

def test_admin_force_deregister_success():
    user_id = uuid4() 
    course_id = uuid4() 
    
    new_student = UserResponse(id=user_id, name="John", email="john@gmail.com", role="student", created_at=datetime.now(timezone.utc)) # type: ignore
    new_course = CourseResponse(id=course_id, code="CSC500", title="Software Engineering", created_at=datetime.now(timezone.utc)) # type: ignore

    users_db[user_id] = new_student
    courses_db[course_id] = new_course

    enrollment = EnrollmentService.enroll_student(user_id, course_id)
    assert enrollment.id in enrollments_db
    result = EnrollmentService.admin_force_deregister(user_id, course_id)
    assert result["message"] == "Student successfully deregistered by admin."
