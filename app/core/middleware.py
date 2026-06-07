from datetime import datetime, time
from time import perf_counter
import uuid
from fastapi import Request
from app.core.logging_config import logger
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start   = perf_counter()
        start_dt = datetime.now()
        
        response = await call_next(request)

        duration_ms = (perf_counter() - start) * 1000  # ms
        response.headers["X-Request-ID"]   = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "timestamp_start": start_dt.isoformat(),
            }
        )
        return response