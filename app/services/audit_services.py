from fastapi import HTTPException, status
from app.repositories.audit_repository import AuditLogRepository
from app.schemas.audit_schema import AuditLogResponse

class AuditLogService:
    @staticmethod
    async def list_audit_logs(
        db,
        *,
        current_user,
        action: str | None = None,
        page: int = 1,
        limit: int = 20
    ):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        skip = (page - 1) * limit
        logs = await AuditLogRepository.list_logs(
            db,
            action=action,
            skip=skip,
            limit=limit
        )
        total = await AuditLogRepository.count_logs(
            db,
            action=action
        )
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": [AuditLogResponse.model_validate(log) for log in logs]
        }