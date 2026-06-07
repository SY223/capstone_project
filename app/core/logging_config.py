import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        skip = {
            "args", "msg", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno",
            "funcName", "created", "msecs", "relativeCreated", "thread",
            "threadName", "processName", "process",
        }
        for key, value in record.__dict__.items():
            if key not in skip:
                try:
                    json.dumps(value)
                    log[key] = value
                except Exception:
                    log[key] = str(value)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers = [handler]

    for name in logging.root.manager.loggerDict:
        if name.startswith("celery"):
            logging.getLogger(name).handlers = [handler]
            logging.getLogger(name).propagate = True

logger = logging.getLogger("Enrolment_API")
