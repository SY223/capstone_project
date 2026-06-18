import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.course_model import Course
    from app.models.enrollment_model import Enrollment

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"),nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    enrollment_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("enrollments.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    audit_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, name="action_metadata", nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    course: Mapped[Optional["Course"]] = relationship("Course", lazy="selectin")
    enrollment: Mapped[Optional["Enrollment"]] = relationship("Enrollment", lazy="selectin")