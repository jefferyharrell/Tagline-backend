import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from alembic import context
from tagline_backend_app.config import get_settings
from tagline_backend_app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Ensure Alembic always has a DB URL, even if DATABASE_URL is unset
config.set_main_option(
    "sqlalchemy.url", os.environ.get("DATABASE_URL") or "sqlite:///./tagline.db"
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode using the DATABASE_URL from app config.
    This configures the context with just a URL (no Engine), so DBAPI is not required.
    """
    settings = get_settings()
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using the DATABASE_URL from app config.
    This creates an Engine and associates a connection with the context.
    """
    config_section = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
