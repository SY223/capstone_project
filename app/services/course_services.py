
from uuid import uuid4, UUID 
from datetime import datetime
from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate
from app.core.db import courses_db


class CourseService:
    @staticmethod
    def create_course(course_create: CourseCreate):
        if not course_create.title or not course_create.title.strip():
            raise ValueError("Course title is required")
        if not course_create.code or not course_create.code.strip():
            raise ValueError("Course code is required")
        #unique code validation
        for course in courses_db.values():
            if course.code.lower() == course_create.code.lower():
                raise ValueError("Course code already exists")
        new_course = CourseResponse(
            id=uuid4(),
            code=course_create.code.upper(),
            title=course_create.title,
            created_at=datetime.utcnow()
        )
        courses_db[new_course.id] = new_course
        return new_course
    
    @staticmethod
    def get_all_courses():
        courses = list(courses_db.values())
        if not courses:
            raise ValueError("No courses available")
        return courses
    
    @staticmethod
    def get_course(course_id: UUID):
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course not found")
        return course
    
    @staticmethod
    def replace_course(course_id: UUID, course_update: CourseCreate):
        course = courses_db.get(course_id)
        if course is None:
            raise ValueError("Course not found")
        if not course_update.title or not course_update.title.strip():
            raise ValueError("Course title is required")
        if not course_update.code or not course_update.code.strip():
            raise ValueError("Course code is required")
        #check unique course code
        if course_update.code is not None:
            for c in courses_db.values():
                if c.id != course_id and c.code.lower() == course_update.code.lower():
                    raise ValueError(f"Course code '{course_update.code}' is already assigned to another course.")
        course.updated_at = datetime.utcnow()
        course.code = course_update.code.upper()
        course.title = course_update.title
        courses_db[course_id] = course
        return course
        
    @staticmethod
    def partial_update_course(course_id: UUID, course_update: CourseUpdate):
        course = courses_db.get(course_id)
        if course is None:
            raise ValueError("Course not found")
        if course_update.title:
            course.title = course_update.title.strip()
        if course_update.code:
            course.code = course_update.code.strip()
        course.updated_at = datetime.utcnow()
        courses_db[course_id] = course
        return course

    @staticmethod
    def delete_course(course_id: UUID):
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course not found.")
        del courses_db[course_id]

    





