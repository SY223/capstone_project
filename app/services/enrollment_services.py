from fastapi import Depends, HTTPException
from uuid import uuid4, UUID
from typing import List, Dict
from app.core.db import users_db, courses_db, enrollments_db
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentDetails, EnrollmentResponse, EnrollmentRequest
from app.api.deps import is_student_user
from app.schemas.course_schema import CourseResponse
from app.schemas.user_schema import UserRole, UserResponse
from app.services.user_services import UserService
from datetime import datetime, timezone

class EnrollmentService:
    @staticmethod
    def enroll_student(user_id: UUID, course_id: UUID):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User does not exist")
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        #prevent duplicate enrollment
        for e in enrollments_db.values():
            if e.user_id == user.id and e.course_id == course.id:
                raise ValueError("Student is already enrolled in this course")
        new_id = uuid4()
        enrollment_in_db = EnrollmentResponse(
            id=new_id,
            user_id=user.id,
            course_id=course.id,
            enrolled_on=datetime.now(timezone.utc)
        )
        enrollments_db[enrollment_in_db.id] = enrollment_in_db
        return enrollment_in_db

    @staticmethod
    def retrieve_student_enrollments(user_id: UUID) -> List[CourseResponse]:
        user = users_db.get(user_id) 
        if not user: 
            raise ValueError("User does not exist") 
        if user.role != UserRole.STUDENT: 
            raise ValueError("Only students can enroll in courses") 
        results: List[EnrollmentResponse] = [] 
        # Loop through all enrollments 
        for enrollment in enrollments_db.values():
            if str(enrollment.user_id) != str(user_id): 
                continue 
            results.append(enrollment)
        if not results:
            raise ValueError("No enrollments found.")
        return results # type: ignore

    @staticmethod
    def student_deregister(user_id: UUID, course_id: UUID):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User does not exist")
        
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        enrollment_to_delete = None

        for enrollment_id, enrollment in enrollments_db.items(): 
            if enrollment.user_id == user_id and enrollment.course_id == course_id: 
                enrollment_to_delete = enrollment_id 
                break
        if not enrollment_to_delete: 
            raise ValueError("Enrollment not found")
        del enrollments_db[enrollment_to_delete]
        return {
            "message": "Successfully deregister from the course."
        }
        
    @staticmethod
    def admin_retrieve_enrollments() -> List[EnrollmentDetails]:
        results: List[EnrollmentDetails] = []
        for enrollment in enrollments_db.values():
            student = users_db.get(enrollment.user_id)
            course = courses_db.get(enrollment.course_id)
            if not student or not course: 
                continue 
            results.append(EnrollmentDetails(
                id=enrollment.id, 
                student=student, 
                course=course, 
                enrolled_on=enrollment.enrolled_on
            ))
        if not results:
            raise ValueError("No enrollments found.")
        return results
    
    @staticmethod
    def admin_retrieve_course_enrollments(course_id: UUID):
        results = []
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        for enrollment in enrollments_db.values():
            if enrollment.course_id != course_id:
                continue
            student = users_db.get(enrollment.user_id)
            if not student:
                continue
            results.append(
                EnrollmentDetails(
                    id=enrollment.id,
                    student=student,
                    course=course,
                    enrolled_on=enrollment.enrolled_on
                )
            )
        if not results:
            raise ValueError(f"No enrollments found for this course {course.title}.")
        return results

    @staticmethod
    def admin_force_deregister(user_id: UUID, course_id: UUID):
        student = users_db.get(user_id)
        if not student:
            raise ValueError("Student does not exist")
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        
        for enrollment in list(enrollments_db.values()):
            if enrollment.user_id == user_id and enrollment.course_id == course_id:
                del enrollments_db[enrollment.id]
            return {"message": "Student successfully deregistered by admin."}

        raise ValueError("Enrollment not found")


            
