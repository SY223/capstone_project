from app.models.user_model import User
from app.core.enums import UserRole
from app.core.security import hash_password

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
