from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt
from app.core.config import settings

def create_test_token(user_id: UUID):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
