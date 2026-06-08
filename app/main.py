import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import FastAPI, Request, Response
from app.api.v1.users import user_router
from app.api.v1.auth import auth_router
from app.api.v1.courses import course_router
from app.api.v1.enrollments import enrollment_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, logger
from app.core.middleware import TimingMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiter import limiter
from app.core.rate_limit_handler import rate_limit_handler





setup_logging()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0, #In production this should be 0.1
        profiles_sample_rate=1.0
    )
    
logger.info("FastAPI started successfully")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="This is the API documentation for the Enrollment system.",
    version="1.0.0"
)

#MIDDLEWARE
app.add_middleware(TimingMiddleware)

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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication Routes"])
app.include_router(user_router, prefix="/api/v1/users", tags=["User Routes"])
app.include_router(course_router, prefix="/api/v1/courses", tags=["Course Routes"])
app.include_router(enrollment_router, prefix="/api/v1/enrollments", tags=["Enrollment Routes"])

@app.get("/")
def root():
    return {
        "message": "A mini social feed API working perfectly!"
    }
    
@app.get("/sentry-test")
async def sentry_test():
    division_by_zero = 1/0




