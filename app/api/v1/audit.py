
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.audit_services import AuditLogService
from app.core.deps import get_async_db, auth_get_current_user
from app.schemas.user_schema import UserResponse

audit_router = APIRouter()

@audit_router.get("/")
async def admin_list_audit_logs(
    action: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserResponse = Depends(auth_get_current_user)
):
    return await AuditLogService.list_audit_logs(
        db,
        current_user=current_user,
        action=action,
        page=page,
        limit=limit
    )


