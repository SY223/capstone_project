import pytest
from uuid import uuid4
from tests.utils.factories import create_user, create_admin, create_teacher, create_course, create_student
from tests.utils.auth import create_test_token


@pytest.mark.asyncio
async def test_teacher_can_create_course(client, db_session):
    teacher = await create_teacher(db_session)
    token = create_test_token(teacher.id)

    payload = {
        "title": "Mathematics",
        "code": "MAT101",
        "capacity": 40
    }

    response = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "mathematics"
    assert data["code"] == "MAT101"
    assert data["capacity"] == 40
    
@pytest.mark.asyncio
async def test_teacher_cannot_delete_course(client, db_session):
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    token = create_test_token(teacher.id)

    response = await client.delete(
        f"/api/v1/courses/{course.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_course_invalid_code(client, db_session):
    teacher = await create_teacher(db_session)
    token = create_test_token(teacher.id)

    payload = {
        "title": "Bad Code",
        "code": "INVALID",
        "capacity": 20
    }

    response = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_course_missing_fields(client, db_session):
    teacher = await create_teacher(db_session)
    token = create_test_token(teacher.id)

    payload = {
        "title": "Missing Code"
        # code missing
    }

    response = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_courses_pagination(client, db_session):
    teacher = await create_teacher(db_session)

    for i in range(5):
        await create_course(
            db_session,
            teacher_id=teacher.id,
            title=f"Course {i}",
            code=f"CRS{i}01"
        )

    response = await client.get("/api/v1/courses/?page=0&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5

@pytest.mark.asyncio
async def test_duplicate_course_code_fails(client, db_session):
    teacher = await create_teacher(db_session)
    token = create_test_token(teacher.id)

    await create_course(db_session, teacher_id=teacher.id, code="DUP101")

    payload = {
        "title": "Another Course",
        "code": "DUP101",
        "capacity": 20
    }

    response = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_student_cannot_create_course(client, db_session):
    student = await create_student(db_session)
    token = create_test_token(student.id)

    payload = {
        "title": "Introduction to Physics",
        "code": "PHY101",
        "capacity": 40
    }

    response = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    
@pytest.mark.asyncio
async def test_public_can_list_active_courses(client, db_session):
    teacher = await create_teacher(db_session)
    await create_course(db_session, teacher_id=teacher.id, title="Biology", code="BIO101")
    await create_course(db_session, teacher_id=teacher.id, title="Chemistry", code="CHE101")

    response = await client.get("/api/v1/courses/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    
@pytest.mark.asyncio
async def test_admin_can_list_all_courses(client, db_session):
    admin = await create_admin(db_session)
    teacher = await create_teacher(db_session)

    await create_course(db_session, teacher_id=teacher.id, title="History", code="HST101")
    await create_course(db_session, teacher_id=teacher.id, title="Geography", code="GED101")

    token = create_test_token(admin.id)

    response = await client.get(
        "/api/v1/courses/admin/all",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_teacher_can_update_own_course(client, db_session):
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id, title="Old Title", code="OLD101")

    token = create_test_token(teacher.id)

    payload = {"title": "New Title"}

    response = await client.patch(
        f"/api/v1/courses/{course.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "new title"
    

@pytest.mark.asyncio
async def test_teacher_cannot_update_other_teachers_course(client, db_session):
    teacher1 = await create_teacher(db_session)
    teacher2 = await create_teacher(db_session)

    course = await create_course(db_session, teacher_id=teacher1.id, title="Credit History Management", code="CRS101")

    token = create_test_token(teacher2.id)

    payload = {"title": "Principles of Driving"}

    response = await client.patch(
        f"/api/v1/courses/{course.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data.get('detail') == 'You are not the owner of this course'
    
@pytest.mark.asyncio
async def test_admin_can_delete_course(client, db_session):
    admin = await create_admin(db_session)
    teacher = await create_teacher(db_session)

    course = await create_course(db_session, teacher_id=teacher.id, title="Delete Training", code="DEL101")

    token = create_test_token(admin.id)

    response = await client.delete(
        f"/api/v1/courses/{course.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200 or response.status_code == 204
    

@pytest.mark.asyncio
async def test_admin_can_deactivate_course(client, db_session):
    admin = await create_admin(db_session)
    teacher = await create_teacher(db_session)

    course = await create_course(db_session, teacher_id=teacher.id, title="Active", code="ACT101")

    token = create_test_token(admin.id)

    response = await client.patch(
        f"/api/v1/courses/{course.id}/deactivate",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
@pytest.mark.asyncio
async def test_admin_can_reactivate_course(client, db_session):
    admin = await create_admin(db_session)
    teacher = await create_teacher(db_session)

    course = await create_course(
        db_session,
        teacher_id=teacher.id,
        title="Inactive",
        code="INA101",
        is_active=False
    )

    token = create_test_token(admin.id)

    response = await client.patch(
        f"/api/v1/courses/{course.id}/reactivate",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_teacher_can_fully_replace_course(client, db_session):
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    token = create_test_token(teacher.id)

    payload = {
        "title": "Replaced Course",
        "code": "NEW101"
    }

    response = await client.put(
        f"/api/v1/courses/{course.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "replaced course"
    assert data["code"] == "NEW101"
    

