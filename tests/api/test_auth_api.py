from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.core.enums import UserRole
from app.core.security import create_access_token
from tests.utils.factories import create_user
from tests.utils.auth import create_test_token

@pytest.mark.asyncio
async def test_register_user(client, db_session):
    payload = {
        "email": "newuser@test.com",
        "full_name": "New User",
        "role": "student",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    
@pytest.mark.asyncio
async def test_login_success(client, db_session):
    user = await create_user(db_session, email="login@test.com")
    user.is_verified = True
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
@pytest.mark.asyncio
async def test_login_unverified_user(client, db_session):
    await create_user(db_session, email="unverified@test.com", is_verified=False)

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "unverified@test.com", "password": "password123"}
    )

    assert response.status_code == 400
    assert "verify" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_invalid_password(client, db_session):
    user = await create_user(db_session, email="wrongpw@test.com")
    user.is_verified = True
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw@test.com", "password": "incorrect"}
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()
    
@pytest.mark.asyncio
async def test_verify_email_success(client, db_session):
    user = await create_user(
        db_session,
        email="verify@test.com",
        is_verified=False, 
        with_verification_code=True
    )
    payload = {
        "email": "verify@test.com",
        "code": user.verification_code
    }

    response = await client.post("/api/v1/auth/verify-email", json=payload)
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()
    
@pytest.mark.asyncio
async def test_verify_email_invalid_code(client, db_session):
    user = await create_user(
        db_session,
        email="invalidcode@test.com",
        is_verified=False, 
        with_verification_code=True
    )

    payload = {
        "email": "invalidcode@test.com",
        "code": "999999"  # wrong code
    }

    response = await client.post("/api/v1/auth/verify-email", json=payload)
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()
    

@pytest.mark.asyncio
async def test_verify_email_expired_code(client, db_session):
    user = await create_user(
        db_session, 
        email="expired@test.com",
        is_verified=False, 
        with_verification_code=True
    )
    # Assume the code expired
    user.verification_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.commit()
    payload = {
        "email": "expired@test.com",
        "code": user.verification_code
    }
    response = await client.post("/api/v1/auth/verify-email", json=payload)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
    

@pytest.mark.asyncio
async def test_get_current_user(client, db_session):
    user = await create_user(db_session, email="me@test.com")
    user.is_verified = True
    await db_session.commit()

    token = create_test_token(user.id)

    response = await client.post(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"

@pytest.mark.asyncio
async def test_refresh_token(client, db_session):
    user = await create_user(db_session, email="refresh@test.com")
    user.is_verified = True
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@test.com", "password": "password123"}
    )
    refresh_token = login_res.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    
@pytest.mark.asyncio
async def test_logout(client, db_session):
    user = await create_user(db_session, email="logout@test.com")
    user.is_verified = True
    await db_session.commit()

    token = create_test_token(user.id)

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_logout_all(client, db_session):
    user = await create_user(
        db_session,
        email="logoutall@test.com",
        role=UserRole.admin,
        is_verified=True,
        is_active=True
    )
    await db_session.commit()
    token_data = {
        "sub": str(user.id), 
        "role": user.role
    }
    
    token = create_access_token(data=token_data)
    response = await client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_password_reset_request(client, db_session):
    await create_user(db_session, email="reset@test.com")

    response = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "reset@test.com"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_password_reset_confirm(client, db_session):
    user = await create_user(db_session, email="reset2@test.com")
    user.reset_token = "123456"
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    payload = {
        "email": "reset2@test.com",
        "code": user.reset_token,
        "new_password": "NewPassword123!"
    }
    response = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json=payload
    )
    print("🚨 PASSWORD RESET CONFIRM ERROR:", response.json())
    assert response.status_code == 200
