from celery import Celery
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from celery.signals import after_setup_logger
from app.core.config import settings
from app.core.logging_config import setup_logging, logger


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[CeleryIntegration()],
        traces_sample_rate=1.0,
    )
    
@after_setup_logger.connect
def setup_celery_logging(logger, *args, **kwargs):
    setup_logging(level="INFO")

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_BROKER,
    backend=settings.REDIS_BACKEND,
    include=["app.tasks.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True
)

