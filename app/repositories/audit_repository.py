from typing import Any, Dict

from sqlalchemy import desc, func, select
from app.models.audit_model import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession


class AuditLogRepository:
    @staticmethod
    async def log(
        db: AsyncSession,
        *,
        user_id: str,
        action: str,
        course_id: str | None = None,
        enrollment_id: str | None = None,
        metadata: Dict[str, Any] | None = None 
    ):
        entry = AuditLog(
            user_id=user_id,
            action=action,
            course_id=course_id,
            enrollment_id=enrollment_id,
            metadata=metadata or {}
        )
        db.add(entry)
        await db.flush()
        return entry
    
    @staticmethod
    async def list_logs(
        db: AsyncSession,
        *,
        action: str | None = None,
        skip: int = 0,
        limit: int = 20
    ):
        query = select(AuditLog).order_by(desc(AuditLog.timestamp))
        if action:
            query = query.where(AuditLog.action == action)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def count_logs(
        db: AsyncSession,
        *,
        action: str | None = None
    ):
        query = select(func.count(AuditLog.id))
        if action:
            query = query.where(AuditLog.action == action)
        result = await db.execute(query)
        return result.scalar_one()
        