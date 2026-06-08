from app.models.user_model import User
from app.core.enums import UserRole
from app.core.security import hash_password
from app.models.course_model import Course
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime, timezone

async def create_user(db, *, email, role=UserRole.student, active=True):
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=hash_password("password123"),
        role=role,
        is_active=active
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_admin(db):
    return await create_user(
        db,
        email="admin@test.com",
        role=UserRole.admin,
        active=True
    )

async def create_teacher(db, email: str | None = None):
    teacher_email = email or f"teacher_{uuid4().hex[:6]}@test.com"

    return await create_user(
        db,
        email=teacher_email,
        role=UserRole.teacher,
    )

async def create_student(db, email: str | None = None):
    student_email = email or f"student_{uuid4().hex[:6]}@test.com"

    return await create_user(
        db,
        email=student_email,
        role=UserRole.student,
    )

async def create_course(
    db,
    *,
    teacher_id,
    title: str = "Sample Course",
    code: str | None = None,
    capacity: int = 40,
    is_active: bool = True
):
    final_code = code or f"CRS{uuid4().hex[:4].upper()}"

    course = Course(
        id=uuid4(),
        title=title.lower(),
        code=final_code,
        capacity=capacity,
        is_active=is_active,
        owner_id=teacher_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course

