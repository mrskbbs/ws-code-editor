"""Fixtures for websocket tests.

httpx's ASGI transport (used for the HTTP tests) does not speak the websocket
protocol, so websocket tests use Starlette/FastAPI's ``TestClient`` instead,
which drives the ASGI app over an in-process websocket using a background
thread + portal. This conftest provides that client plus the same DB override
the HTTP ``client`` fixture uses, so websocket handlers see the test database.

Everything here is imported lazily and the websocket tests are skipped until the
``/rooms/{id}/ws`` endpoint exists, so importing this module never requires the
(currently incomplete) websocket route to be importable.
"""

import os
import sys

import pytest

# The parent ``tests/conftest.py`` puts the backend root and the tests dir on
# ``sys.path`` (so ``import app`` / ``import factories`` work). Re-do it here so
# these tests import cleanly even when collected directly (e.g.
# ``pytest tests/ws/test_room_ws.py``) and the parent conftest hasn't been
# loaded yet.
_TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.dirname(_TESTS_DIR)
for _path in (_BACKEND_DIR, _TESTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from app.db import getDb


@pytest.fixture
def ws_client(engine):
    """A synchronous ``TestClient`` for exercising websocket routes.

    Use it like::

        with ws_client.websocket_connect(
            f"/rooms/{room_id}/ws", cookies=auth_cookies(user.id)
        ) as ws:
            ws.send_json({"type": "code", "code": "print(1)"})
            assert ws.receive_json()["code"] == "print(1)"

    Note this fixture is synchronous (TestClient is sync); async ``db`` setup
    should be done in the test body before opening the connection, or via the
    async fixtures from the parent ``conftest``.

    The DB override deliberately does *not* reuse the parent ``sessionmaker_``:
    that engine is bound to pytest's event loop, whereas ``TestClient`` runs the
    app in its own portal-thread loop, and ``asyncpg`` connections are pinned to
    the loop that created them (sharing one engine raises "Future attached to a
    different loop"). Instead each request gets a throwaway ``NullPool`` engine
    created inside the app's loop, pointed at the same test database — so it
    sees the rows the test's ``db`` session has committed. Depending on
    ``engine`` (not ``sessionmaker_``) is only to guarantee the schema exists.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from app.config import TESTS_DB_URL
    from app.main import app as fastapi_app

    async def _override_get_db():
        request_engine = create_async_engine(TESTS_DB_URL, poolclass=NullPool)
        try:
            maker = async_sessionmaker(request_engine, expire_on_commit=False)
            async with maker() as session:
                yield session
        finally:
            await request_engine.dispose()

    fastapi_app.dependency_overrides[getDb] = _override_get_db
    try:
        with TestClient(fastapi_app) as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture
def manager(ws_client):
    """The live ``WSRoomManager`` the app is using, reached through the app
    under test (``app.state.room_manager``) rather than by importing the module.

    Each ``ws_client`` builds a fresh ``TestClient``, whose lifespan creates a
    fresh manager, so this is naturally isolated per test — no global reset
    needed. Tests use it for the in-memory "room created / deleted" assertions;
    everything else is asserted through the websocket protocol itself.
    """
    return ws_client.app.state.room_manager
