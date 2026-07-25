"""
MuleTrace AI — Alembic Migration Environment.

This script is executed by Alembic when running migrations.
It discovers all SQLAlchemy models via Base.metadata and uses
the sync PostgreSQL DSN from settings.

IMPORTANT:
    All model files MUST be imported below so that Alembic can
    detect their tables. If you add a new model, import it here.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config.settings import settings
from app.database.base import Base

# ---------------------------------------------------------------------------
# Import ALL models here so Alembic can detect them.
# Add new model imports as they are created.
# ---------------------------------------------------------------------------
from app.models.account import Account  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.atm import ATM  # noqa: F401
from app.models.beneficiary import Beneficiary  # noqa: F401
from app.models.branch import Branch  # noqa: F401
from app.models.case import Case  # noqa: F401
from app.models.device import Device  # noqa: F401
from app.models.ip_address import IPAddress  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.rule import Rule  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to alembic.ini values.
# ---------------------------------------------------------------------------
config = context.config

# Set the SQLAlchemy URL from settings, escaping % for ConfigParser
config.set_main_option("sqlalchemy.url", settings.postgres_dsn_sync.replace("%", "%%"))

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Useful for reviewing migration SQL before applying.

    Usage:
        alembic upgrade head --sql
    """
    url = settings.postgres_dsn_sync
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations directly.
    This is the standard migration workflow.

    Usage:
        alembic upgrade head
    """
    connectable = create_engine(
        settings.postgres_dsn_sync,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Execute the appropriate migration mode.
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
