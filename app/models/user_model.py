import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.core.db_async import Base
from enum import Enum


if TYPE_CHECKING:
    from app.models.course_model import Course
    from app.models.enrollment_model import Enrollment
    from app.models.auth_model import RefreshToken





class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True),primary_key=True, default=uuid.uuid4, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), default=UserRole.student, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    #Relationships
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="owner", lazy="selectin")
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="student", lazy="selectin")
    # For password reset
    reset_token:Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reset_token_expiry:Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", lazy="selectin")


    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.teacher

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.student

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin
