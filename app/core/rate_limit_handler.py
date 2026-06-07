from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logging_config import logger
from app.core.deps import get_client_ip

async def rate_limit_handler(request: Request, exc: Exception):
    logger.warning(
        "rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "ip": get_client_ip(request)
        }
    )

    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )