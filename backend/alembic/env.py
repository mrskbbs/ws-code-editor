import logging
from logging.config import fileConfig
import re

from sqlalchemy import MetaData, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import os
from dotenv import load_dotenv
import asyncio

load_dotenv(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        ".env",
    )
)

from app.db import Base
import app.db.models

DB_URL = os.environ["DB_URL"]
TESTS_DB_URL = os.environ["TESTS_DB_URL"]

USE_TWOPHASE = False

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Inject the URLs from the environment into the per-database sections
# BEFORE we read those sections to build engines.
config.set_section_option("main_db", "sqlalchemy.url", DB_URL)
config.set_section_option("tests_db", "sqlalchemy.url", TESTS_DB_URL)

# gather section names referring to different databases.
db_names = config.get_main_option("databases", "")

# Model MetaData per database, for 'autogenerate' support.
target_metadata = {
    "main_db": Base.metadata,
    "tests_db": Base.metadata,
}


def _iter_db_names():
    """Yield non-empty, stripped database section names."""
    return [n for n in re.split(r",\s*", db_names) if n]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    so we don't even need a DBAPI to be available.
    """
    # for the --sql use case, run migrations for each URL into
    # individual files.
    engines = {}
    for name in _iter_db_names():
        engines[name] = rec = {}
        rec["url"] = context.config.get_section_option(name, "sqlalchemy.url")

    for name, rec in engines.items():
        logger.info("Migrating database %s" % name)
        file_ = "%s.sql" % name
        logger.info("Writing output to %s" % file_)
        with open(file_, "w") as buffer:
            context.configure(
                url=rec["url"],
                output_buffer=buffer,
                target_metadata=target_metadata.get(name),
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )
            with context.begin_transaction():
                context.run_migrations(engine_name=name)


def do_run_migrations(connection, name):
    """Synchronous migration body, executed via run_sync per engine."""
    context.configure(
        connection=connection,
        upgrade_token="%s_upgrades" % name,
        downgrade_token="%s_downgrades" % name,
        target_metadata=target_metadata.get(name),
    )
    context.run_migrations(engine_name=name)


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async engines).

    Start a transaction on all engines, run all migrations,
    then commit all transactions.
    """
    engines = {}
    for name in _iter_db_names():
        engines[name] = rec = {}
        rec["engine"] = async_engine_from_config(
            context.config.get_section(name, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    for name, rec in engines.items():
        engine = rec["engine"]
        rec["connection"] = conn = await engine.connect()
        if USE_TWOPHASE:
            rec["transaction"] = await conn.begin_twophase()
        else:
            rec["transaction"] = await conn.begin()

    try:
        for name, rec in engines.items():
            logger.info("Migrating database %s" % name)
            await rec["connection"].run_sync(do_run_migrations, name)

        if USE_TWOPHASE:
            for rec in engines.values():
                await rec["transaction"].prepare()

        for rec in engines.values():
            await rec["transaction"].commit()
    except:
        for rec in engines.values():
            await rec["transaction"].rollback()
        raise
    finally:
        for rec in engines.values():
            await rec["connection"].close()
        for rec in engines.values():
            await rec["engine"].dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
