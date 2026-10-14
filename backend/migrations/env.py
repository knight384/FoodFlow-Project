"""
Alembic migration environment.

Reads the database connection string from the application's own
environment-based configuration (app.config.get_settings) rather than
duplicating it in alembic.ini — consistent with TRD v1.0 Section 21
(no secrets/connection strings committed to source control) and
Database Specification v1.0 Section 25 (Migration Strategy: schema
changes tracked, repeatable across environments).

`target_metadata` points at the shared declarative Base
(app.database.Base), populated via app.models_registry, so
`alembic revision --autogenerate` can compare the database against all
currently-defined ORM models.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure every model is imported (and therefore registered on Base.metadata)
# before Alembic inspects it.
from app.database import Base
from app import models_registry  # noqa: F401 - import registers all models
from app.config import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Inject the application's DATABASE_URL into Alembic's config at runtime,
# rather than hardcoding it in alembic.ini.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL only)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
