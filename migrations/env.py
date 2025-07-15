from __future__ import with_statement
import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Dynamically compute and append absolute path to 'src' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

from src.extensions import db  # SQLAlchemy instance
from src.main import create_app  # Flask app factory

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name:
    fileConfig(config.config_file_name)

# Provide metadata object for 'autogenerate' support
target_metadata = db.metadata

# Initialize app and set context
app = create_app()

with app.app_context():

    def run_migrations_offline():
        url = app.config.get("SQLALCHEMY_DATABASE_URI")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        section = config.get_section(config.config_ini_section)
        if section is None:
            raise RuntimeError("Missing configuration section in Alembic config")

        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
