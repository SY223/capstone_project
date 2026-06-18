from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    course_id: Optional[UUID]
    enrollment_id: Optional[UUID]
    timestamp: datetime
    audit_metadata: Optional[Dict] = None

    class Config:
        from_attributes = True