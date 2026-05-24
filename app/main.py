from fastapi import FastAPI
from app.api.v1.users import user_router
from app.api.v1.courses import course_router
from app.api.v1.enrollments import enrollment_router


app = FastAPI()

app.include_router(user_router, prefix="/api/v1/users", tags=["User Routes"])
app.include_router(course_router, prefix="/api/v1/courses", tags=["Course Routes"])
app.include_router(enrollment_router, prefix="/api/v1/enrollments", tags=["Student Enrollments Routes"])

app.get("/")
def root():
    return {
        "message": "A mini social feed API working perfectly!"
    }

