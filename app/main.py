from fastapi import FastAPI, Request, Response
from app.api.v1.users import user_router
from app.api.v1.auth import auth_router
from app.api.v1.courses import course_router
from app.api.v1.enrollments import enrollment_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

#MIDDLEWARE
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Optional but recommended
    #response.headers["Content-Security-Policy"] = "default-src 'self';"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication Routes"])
app.include_router(user_router, prefix="/api/v1/users", tags=["User Routes"])
app.include_router(course_router, prefix="/api/v1/courses", tags=["Course Routes"])
app.include_router(enrollment_router, prefix="/api/v1/enrollments", tags=["Enrollment Routes"])

app.get("/")
def root():
    return {
        "message": "A mini social feed API working perfectly!"
    }




