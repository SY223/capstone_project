import pytest 
from fastapi.testclient import TestClient 
from uuid import uuid4 
from app.main import app
from app.core.db_async import users_db, courses_db, enrollments_db

client = TestClient(app)

