import pytest
from tests.utils.factories import create_user, create_admin
from tests.utils.auth import create_test_token



@pytest.mark.asyncio
async def test_admin_can_list_active_users(client, db_session):
    admin = await create_admin(db_session)
    user1 = await create_user(db_session, email="userone@test.com")
    user2 = await create_user(db_session, email="usertwo@test.com")

    token = create_test_token(admin.id)
    
    response = await client.get(
        "/api/v1/users/active",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["email"] == "admin@test.com"
    
@pytest.mark.asyncio
async def test_non_admin_cannot_list_active_users(client, db_session):
    user = await create_user(db_session, email="normaluser@test.com")
    token = create_test_token(user.id)

    response = await client.get(
        "/api/v1/users/active",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    
@pytest.mark.asyncio
async def test_admin_get_user_by_id(client, db_session):
    admin = await create_admin(db_session)
    user = await create_user(db_session, email="targetuser@test.com")

    token = create_test_token(admin.id)
    
    response = await client.get(
        f"/api/v1/users/{str(user.id)}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "targetuser@test.com"
    

@pytest.mark.asyncio
async def test_admin_can_update_user(client, db_session):
    admin = await create_admin(db_session)
    user = await create_user(db_session, email="old@test.com")
    
    token = create_test_token(admin.id)
    payload = {"full_name": "Updated Name"}

    response = await client.put(
        f"/api/v1/users/{user.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == user.full_name.lower()
    
@pytest.mark.asyncio
async def test_admin_can_delete_user(client, db_session):
    admin = await create_admin(db_session)
    user = await create_user(db_session, email="delete@test.com")
    
    token = create_test_token(admin.id)
    
    response = await client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204
