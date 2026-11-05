from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context
from app.core.config import settings
from app.core.base import Base
from app.models.user_model import User
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment
from app.models.audit_model import AuditLog
from app.models.auth_model import RefreshToken

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    database_url = settings.DATABASE_URL

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a synchronous database connection."""

    database_url = settings.DATABASE_URL

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online