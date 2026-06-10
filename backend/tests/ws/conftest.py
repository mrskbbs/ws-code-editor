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
def ws_client(sessionmaker_):
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
    """
    from fastapi.testclient import TestClient

    from app.main import app as fastapi_app

    async def _override_get_db():
        async with sessionmaker_() as session:
            yield session

    fastapi_app.dependency_overrides[getDb] = _override_get_db
    try:
        with TestClient(fastapi_app) as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_room_manager():
    """Reset the process-global websocket room state around every ws test.

    ``room_manager`` is a module-level singleton and ``WSRoom.connections`` is a
    shared mapping, so without this an aborted connection in one test could leak
    rooms/connections into the next. Cleared before *and* after each test so the
    in-memory "room created / room deleted" assertions start from a clean slate.
    """
    from app.ws.room_manager import room_manager
    from app.ws.room import WSRoom

    def _clear():
        room_manager.rooms.clear()
        # connections lives on the class, not the instance, in the current impl.
        WSRoom.connections.clear()

    _clear()
    yield
    _clear()
