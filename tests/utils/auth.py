from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt
from app.core.config import settings


def create_test_token(user_id, role="student"):
    payload = {
        "sub": str(user_id),
        "role": str(role),
        "exp": datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)