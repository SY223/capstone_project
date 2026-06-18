# 📘 Course Enrollment Platform API  
### **A Secure, Database‑Backed FastAPI System with Authentication, RBAC, and Full Test Coverage**

This project implements a **real‑world course enrollment backend** using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **JWT authentication**, and **role‑based access control (RBAC)**.  
It includes **complete API functionality**, **database migrations**, and a **comprehensive automated test suite**.

---

## 🚀 Live API (Render Deployment)
Base URL: https://course-enrollment-api-m4iq.onrender.com/docs

---

# 📑 Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [System Architecture](#system-architecture)  
4. [Entities & Data Model](#entities--data-model)  
5. [Authentication & RBAC](#authentication--rbac)  
6. [Project Structure](#project-structure)  
7. [Setup Instructions](#setup-instructions)  
8. [Running Database Migrations](#running-database-migrations)  
9. [Running the Application](#running-the-application)  
10. [Running the Test Suite](#running-the-test-suite)  
11. [API Overview](#api-overview)  
12. [Development Notes](#development-notes)

---

# 📘 Project Overview

This backend system provides:

- Secure **JWT authentication**
- **Role‑based access control** (Admin vs Student)
- **Relational database** with SQLAlchemy ORM
- **Course management**
- **Enrollment management**
- **Administrative oversight**
- **Automated tests** for all endpoints

It simulates a real production backend and follows clean architecture principles.

---

# ✨ Features

### ✅ **User Management**
- Register  
- Login  
- Retrieve authenticated profile  
- Unique email validation  
- Password hashing  
- Active/inactive user handling  

### 🎓 **Course Management**
- Public: list active courses, get course by ID  
- Admin‑only: create, update, activate/deactivate courses  
- Business rules: unique course code, capacity > 0  

### 📝 **Enrollment Management**
- Students can enroll/deregister  
- Prevent duplicate enrollment  
- Prevent enrollment into full or inactive courses  

### 🛠 **Administrative Oversight**
- Admin can view all enrollments  
- Admin can view enrollments for a specific course  
- Admin can remove a student from a course  

### 🔐 **Security**
- JWT authentication  
- RBAC enforced at router level  
- Secure password hashing  

### 🧪 **Testing**
- Full API test suite  
- Unit tests for services  
- Test database (PostgreSQL)  
- Redis mocked for caching tests  

---

# 🏗 System Architecture

```
FastAPI (Routers)
      ↓
Services (Business Logic)
      ↓
Repositories (DB Access)
      ↓
PostgreSQL (Async SQLAlchemy ORM)
```

Additional components:

- **Redis caching** (mocked in tests)
- **Alembic** for migrations
- **Pytest** for automated testing
- **Docker Compose** for local development

---

# 🗄 Entities & Data Model

### **User**
- id  
- full_name  
- email  
- hashed_password  
- role (student/admin)  
- is_active  
- timestamps  

### **Course**
- id  
- title  
- code (unique)  
- capacity  
- is_active  

### **Enrollment**
- id  
- user_id  
- course_id  
- created_at  

---

# 🔐 Authentication & RBAC

### **Authentication**
- JWT access tokens  
- Login returns token  
- Passwords hashed using secure algorithm  

### **Authorization Rules**

| Action | Student | Admin |
|--------|---------|--------|
| View courses | ✅ | ✅ |
| Enroll | ✅ | ❌ |
| Deregister | ✅ | ❌ |
| Create course | ❌ | ✅ |
| Update course | ❌ | ✅ |
| Delete course | ❌ | ✅ |
| View all enrollments | ❌ | ✅ |

---

# 📂 Project Structure

```
app/
 ├── api/
 │    └── v1/
 │         ├── users.py
 │         ├── courses.py
 │         └── enrollments.py
 │    └── deps.py
 ├── core/
 │    ├── db.py
 │    ├── security.py
 │    ├── config.py
 │    └── cache.py
 ├── models/
 │    ├── user_model.py
 │    ├── course_model.py
 │    └── enrollment_model.py
 ├── schemas/
 │    ├── user_schema.py
 │    ├── course_schema.py
 │    └── enrollment_schema.py
 ├── services/
 │    ├── user_services.py
 │    ├── course_services.py
 │    └── enrollment_services.py
 ├── repositories/
 │    ├── user_repository.py
 │    ├── course_repository.py
 │    └── enrollment_repository.py
 ├── tasks/
 │    ├── celery_app.py
 │    └── email_tasks.py
 └── main.py

tests/
 ├── api/
 │    ├── users/
 │    ├── courses/
 │    └── enrollments/
 └── utils/
      ├── factories.py
      ├── auth.py
      └── mock_redis.py
```

---

# ⚙️ Setup Instructions

### **1. Clone the repository**
```bash
git clone <repo-url>
cd capstone_project
```

### **2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure environment variables**
Create a `.env` file:

```
DATABASE_URL=<your_async_database_url>
JWT_SECRET=your-secret
REDIS_URL=redis://localhost:6379
```

---

# 🗃 Running Database Migrations

### **Initialize Alembic**
```bash
alembic init alembic
```

### **Generate migration**
```bash
alembic revision --autogenerate -m "Initial schema"
```

### **Apply migrations**
```bash
alembic upgrade head
```

---

# 🚀 Running the Application

### **Local (without Docker)**
```bash
uvicorn app.main:app --reload
```

### **Docker**
```bash
docker compose up --build
```

API Docs:

- Swagger → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

# 🧪 Running the Test Suite

### **Run all tests**
```bash
pytest
```

### **Verbose output**
```bash
pytest -vv
```

### **Run coverage**
```bash
pytest --cov=app
```

### **Tests include**
- User endpoints  
- Course endpoints  
- Enrollment endpoints  
- RBAC enforcement  
- Validation  
- Error handling  
- Database interactions  
- Redis caching (mocked)  

---

# 🧪 Running Tests in Docker (Recommended)

When running the application using Docker Compose, your tests should also run **inside the API container**, using the dedicated **PostgreSQL test database** (`postgres_test`).

### **1. Start all services (including test DB)**

```bash
docker compose up -d --build
```

This starts:

- `api` (FastAPI)
- `db` (main PostgreSQL)
- `postgres_test` (test PostgreSQL)
- `redis`
- `celery_worker`
- `celery_beat`

---

### **2. Run the full test suite inside the API container**

```bash
docker compose exec api pytest
```

---

### **3. Run tests with verbose output**

```bash
docker compose exec api pytest -vv
```

---

### **4. Run a specific test file**

```bash
docker compose exec api pytest tests/api/users/test_users_api.py
```

---

### **5. Run tests with coverage**

```bash
docker compose exec api pytest --cov=app
```

---

### **6. Run tests in a one‑off ephemeral container (clean environment)**

This does **not** reuse the running API container:

```bash
docker compose run --rm api pytest
```

Useful when you want a clean environment without cached dependencies.

---

### **7. Rebuild the image before testing (if you changed Python code)**

```bash
docker compose build api
docker compose up -d
docker compose exec api pytest
```

---

### **8. If you changed dependencies (requirements.txt)**

```bash
docker compose build --no-cache api
docker compose up -d
docker compose exec api pytest
```
---

# 📡 API Overview

### **Users**
- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- GET `/api/v1/users/me`
- GET `/api/v1/users/{id}` (admin)
- PUT `/api/v1/users/{id}` (admin)
- DELETE `/api/v1/users/{id}` (admin)
- GET `/api/v1/users/active` (admin)

### **Courses**
- GET `/api/v1/courses`
- GET `/api/v1/courses/{id}`
- POST `/api/v1/courses` (admin)
- PUT `/api/v1/courses/{id}` (admin)
- DELETE `/api/v1/courses/{id}` (admin)

### **Enrollments**
- POST `/api/v1/enrollments/{course_id}` (student)
- DELETE `/api/v1/enrollments/{course_id}` (student)
- GET `/api/v1/enrollments` (admin)
- GET `/api/v1/enrollments/course/{course_id}` (admin)
- DELETE `/api/v1/enrollments/admin/{enrollment_id}` (admin)

---

# 🧠 Development Notes

- All passwords hashed using secure algorithm  
- JWT tokens include expiry  
- Database access isolated in repository layer  
- Services contain business logic  
- Routers contain no business logic  
- Tests use a **separate PostgreSQL test database**  
- Redis is mocked for deterministic tests  
- Code follows clean architecture principles  
