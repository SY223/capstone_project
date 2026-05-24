from app.services.course_services import CourseService
from app.core.db import courses_db, users_db, enrollments_db
from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate
from datetime import datetime, timezone
from uuid import uuid4, UUID
import pytest



# ✅ Automatically clear DB before each test
@pytest.fixture(autouse=True)
def clear_users_db():
    courses_db.clear()

def test_course_create():
    course_data = CourseCreate(
        title="Mathematics", 
        code="MTH101" 
    )
    new_course = CourseService.create_course(course_data)
    assert isinstance(new_course, CourseResponse)
    assert new_course.code == "MTH101"
    assert new_course.id in courses_db

def test_create_course_missing_title():
    course_data = CourseCreate(
        title="", 
        code="MTH101" 
    )
    try:
        CourseService.create_course(course_data)
        raised_error = False
    except ValueError as exc:
        raised_error = True
        error_message = str(exc)

    assert raised_error
    assert error_message == "Course title is required"

def test_create_course_missing_code():
    course_data = CourseCreate(
        title="Mathematics", 
        code="" 
    )
    try:
        CourseService.create_course(course_data)
        raised_error = False
    except ValueError as exc:
        raised_error = True
        error_message = str(exc)

    assert raised_error
    assert "Course code is required" in error_message

def test_get_all_courses_success():
    course1 = CourseService.create_course(
        CourseCreate(
            title="Principles of Driving",
            code="drv104"
        )
    )
    course2 = CourseService.create_course(
        CourseCreate(
            title="Fundamentals of Sleeping",
            code="slp105"
        )
    )
    courses = CourseService.get_all_courses()
    assert len(courses) == 2
    assert course1 in courses
    assert course2 in courses
    assert course1.code == "DRV104"
    assert course2.code == "SLP105"

def test_get_course_by_id():
    course_id = uuid4()
    created_course = CourseResponse(
        id=course_id,
        title="Principles of Driving",
        code="drv104",
        created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc)
    )

    courses_db[course_id] = created_course
    result = CourseService.get_course(course_id)
    assert result == created_course
    assert result.id == course_id
    assert isinstance(result.id, UUID)


def test_replace_course():
    course_id = uuid4()
    original = CourseResponse(
        id=course_id,
        title="Principles of Driving",
        code="drv104",
        created_at=datetime.now(timezone.utc),
    )
    courses_db[course_id] = original
    update_data = CourseCreate( 
        title="Advanced Mathematics", 
        code="MTH201" 
    )
    updated = CourseService.replace_course(course_id, update_data)
    assert updated.title.lower() == "advanced mathematics"
    assert updated.code.lower() == "mth201" 
    assert len(updated.code) == 6
    assert updated.updated_at is not None

def test_partial_replace_course():
    course_id = uuid4()
    original = CourseResponse(
        id=course_id,
        title="Principles of Driving",
        code="drv104",
        created_at=datetime.now(timezone.utc),
    )
    courses_db[course_id] = original
    update_data = CourseUpdate( 
        title="Advanced Mathematics"
    )
    updated = CourseService.partial_update_course(course_id, update_data)
    assert updated.title.lower() == "advanced mathematics"
    assert updated.code.lower() == "drv104"
    assert updated.updated_at is not None

def test_delete_course_success(): 
    course_id = uuid4() 
    course = CourseResponse( 
        id=course_id, 
        title="mathematics", 
        code="MTH101", 
        created_at=datetime.now(timezone.utc) 
    ) 
    courses_db[course_id] = course  
    try: 
        CourseService.delete_course(course_id) 
        raised_error = False 
    except Exception: 
        raised_error = True 
    
    assert not raised_error 
    assert course_id not in courses_db

def test_delete_course_not_found():  
    missing_id = uuid4() 
    try: 
        CourseService.delete_course(missing_id) 
        raised_error = False 
    except ValueError as exc:
        raised_error = True 
        error_message = str(exc)
    assert raised_error 
    assert error_message == "Course not found."
 