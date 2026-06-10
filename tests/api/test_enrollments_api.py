import pytest
from uuid import uuid4

from tests.utils.factories import (
    create_user,
    create_teacher,
    create_admin,
    create_course,
)
from tests.utils.auth import create_test_token


@pytest.mark.asyncio
async def test_student_can_enroll_in_course(client, db_session):
    student = await create_user(db_session, email="stud@test.com")
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    token = create_test_token(student.id)

    payload = {"course_id": str(course.id)}

    response = await client.post(
        "/api/v1/enrollments/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == str(course.id)
    assert data["user_id"] == str(student.id)
    
@pytest.mark.asyncio
async def test_student_cannot_enroll_twice(client, db_session):
    student = await create_user(db_session, email="stud2@test.com")
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    token = create_test_token(student.id)

    payload = {"course_id": str(course.id)}

    # First enrollment
    await client.post(
        "/api/v1/enrollments/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Second enrollment
    response = await client.post(
        "/api/v1/enrollments/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    
@pytest.mark.asyncio
async def test_student_can_list_their_enrollments(client, db_session):
    student = await create_user(db_session, email="stud3@test.com")
    teacher = await create_teacher(db_session)

    course1 = await create_course(db_session, teacher_id=teacher.id)
    course2 = await create_course(db_session, teacher_id=teacher.id, code="CRS202")

    token = create_test_token(student.id)

    for course in [course1, course2]:
        await client.post(
            "/api/v1/enrollments/",
            json={"course_id": str(course.id)},
            headers={"Authorization": f"Bearer {token}"}
        )

    response = await client.get(
        "/api/v1/enrollments/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    
@pytest.mark.asyncio
async def test_admin_can_list_all_enrollments(client, db_session):
    admin = await create_admin(db_session)
    student = await create_user(db_session, email="stud4@test.com")
    teacher = await create_teacher(db_session)

    course = await create_course(db_session, teacher_id=teacher.id)

    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course.id)},
        headers={"Authorization": f"Bearer {create_test_token(student.id)}"}
    )

    response = await client.get(
        "/api/v1/enrollments/admin/all",
        headers={"Authorization": f"Bearer {create_test_token(admin.id)}"}
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

    
@pytest.mark.asyncio
async def test_teacher_can_list_enrollments_for_their_course(client, db_session):
    teacher = await create_teacher(db_session)
    student = await create_user(db_session, email="stud5@test.com")

    course = await create_course(db_session, teacher_id=teacher.id)

    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course.id)},
        headers={"Authorization": f"Bearer {create_test_token(student.id)}"}
    )

    response = await client.get(
        f"/api/v1/enrollments/{course.id}",
        headers={"Authorization": f"Bearer {create_test_token(teacher.id)}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    
@pytest.mark.asyncio
async def test_teacher_cannot_list_enrollments_for_other_teacher_course(client, db_session):
    teacher1 = await create_teacher(db_session)
    teacher2 = await create_teacher(db_session)
    student = await create_user(db_session, email="stud6@test.com")

    course = await create_course(db_session, teacher_id=teacher1.id)

    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course.id)},
        headers={"Authorization": f"Bearer {create_test_token(student.id)}"}
    )

    response = await client.get(
        f"/api/v1/enrollments/{course.id}",
        headers={"Authorization": f"Bearer {create_test_token(teacher2.id)}"}
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_student_can_unenroll(client, db_session):
    student = await create_user(db_session, email="stud7@test.com")
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    token = create_test_token(student.id)

    # Enroll
    enroll_res = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course.id)},
        headers={"Authorization": f"Bearer {token}"}
    )
    enrollment_id = enroll_res.json()["id"]

    # Unenroll
    response = await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_admin_can_remove_student_from_course(client, db_session):
    admin = await create_admin(db_session)
    student = await create_user(db_session, email="stud10@test.com")
    teacher = await create_teacher(db_session)
    course = await create_course(db_session, teacher_id=teacher.id)

    enroll_res = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course.id)},
        headers={"Authorization": f"Bearer {create_test_token(student.id)}"}
    )
    enrollment_id = enroll_res.json()["id"]

    response = await client.delete(
        f"/api/v1/enrollments/admin/remove/{enrollment_id}",
        headers={"Authorization": f"Bearer {create_test_token(admin.id)}"}
    )
    assert response.status_code == 200