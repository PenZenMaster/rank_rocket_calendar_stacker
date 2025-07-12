from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extensions import db  # type: ignore[import]

# Explicitly import models so they are registered in metadata
from src.models.client import Client  # type: ignore[import]
from src.models.oauth import OAuthCredential  # type: ignore[import]

# Alembic Config object
config = context.config

# Configure loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use Flask-SQLAlchemy metadata for migrations
target_metadata = db.metadata

# Database URL is read from alembic.ini


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    from typing import cast, Dict, Any

    raw_section = config.get_section(config.config_ini_section)
    section = cast(Dict[str, Any], raw_section or {})

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
