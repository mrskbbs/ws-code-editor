"""
Core test fixtures for the backend test-suite.

Design goals
------------
* **Isolated**: every test runs against a freshly created schema in the
  ``TESTS_DB_URL`` database. Tables are dropped + recreated per test, so tests
  never see each other's data and order never matters.
* **Self-contained**: the app's real ``getDb`` dependency is overridden so that
  request handlers talk to the same test database/session factory the test code
  uses. No production database is ever touched.
* **Extensible**: fixtures are small and composable. Adding a websocket client,
  a seeded-data fixture, or a different isolation strategy later means adding a
  fixture, not rewriting these.

How to run (from the ``backend/`` directory)::

    pip install -r tests/requirements-test.txt
    pytest tests/

See ``tests/README.md`` for more.
"""

import os
import sys

import pytest
import pytest_asyncio

# Make both the backend package root (so ``import app...`` works) and the tests
# directory (so ``import helpers`` / ``import factories`` work) importable no
# matter where pytest is invoked from.
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TESTS_DIR)
for _path in (BACKEND_DIR, TESTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import TESTS_DB_URL
from app.db import Base, getDb

# Importing the models package registers every model on ``Base.metadata`` so
# that ``create_all`` knows about all tables. NB: this intentionally does *not*
# import the routers/app, so schema-only tests work even while the app module
# is mid-rewrite.
import app.db.models  # noqa: F401


# --------------------------------------------------------------------------- #
# Database / schema
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def engine():
    """A fresh async engine + schema for a single test.

    Drops and recreates every table before the test and drops them again
    afterwards, guaranteeing a clean slate. Function-scoped on purpose: it keeps
    event-loop handling trivial and isolation bullet-proof. If the suite grows
    large enough that per-test DDL hurts, swap this for a session-scoped engine
    plus a transaction-rollback fixture without touching any test.
    """
    eng = create_async_engine(TESTS_DB_URL)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()


@pytest_asyncio.fixture
async def sessionmaker_(engine):
    """An ``async_sessionmaker`` bound to the per-test engine."""
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def db(sessionmaker_):
    """A session for use by test code itself (arranging data, asserting state).

    This is a *separate* session from the one request handlers use, mirroring
    reality: tests observe the database the same way an outside client would.
    """
    async with sessionmaker_() as session:
        yield session


# --------------------------------------------------------------------------- #
# Application / HTTP client
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def app(sessionmaker_):
    """The FastAPI app with ``getDb`` overridden to use the test database.

    Imported lazily so that collecting non-HTTP tests does not require the whole
    app (and its routers) to import cleanly.
    """
    from app.main import app as fastapi_app

    async def _override_get_db():
        async with sessionmaker_() as session:
            yield session

    fastapi_app.dependency_overrides[getDb] = _override_get_db
    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    """An ``httpx.AsyncClient`` wired to the app via in-process ASGI transport.

    No network, no running server. Cookies set by the server are visible on the
    response, but are intentionally *not* replayed automatically (the app scopes
    the auth cookie to ``/api/v1``); tests pass auth cookies explicitly via the
    helpers in ``helpers.py`` so the auth boundary stays obvious in each test.
    """
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
