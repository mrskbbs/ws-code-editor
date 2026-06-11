"""Behavioural tests for the collaborative-room websocket (``/rooms/{id}/ws``).

These describe the *expected* work cycle of the endpoint — the contract the
route is meant to satisfy. Run with::

    pytest tests/ws/

How these tests observe the app
-------------------------------
Everything that can be observed from the outside is asserted through the
websocket protocol itself (the same way a real client sees it): the handshake
succeeding or failing, and the JSON messages that arrive. The one piece of
internal state we look at — whether a room is currently live in memory — is read
through the app under test (``ws_client.app.state.room_manager``, via the
``manager`` fixture), never by importing the manager module. That keeps the
tests coupled to the app's public surface, not to where the manager happens to
live.

Expected protocol
-----------------
A client opens a websocket to ``/rooms/{id}/ws`` authenticated by the same
``auth_token`` cookie the HTTP routes use. Then:

* **Auth gate** — a connection with no / an invalid ``auth_token`` cookie is
  rejected: the handshake fails and the socket closes (surfaces as
  ``WebSocketDisconnect``). For that to happen cleanly the WS auth dependency
  must raise ``WebSocketException`` (not ``HTTPException``) — an HTTP error has
  no meaning once a socket handshake is in progress.
* **Presence** — every message is a ``WSRoomAction`` (``{"action", "data"}``).
  When a member joins, members already connected receive
  ``{"action": "connect", "data": {"id": .., "username": ..}}``; when a member
  leaves, the rest receive ``{"action": "disconnect", "data": {...}}``. A joiner
  gets no presence message about itself.
* **Edit broadcast** — a JSON action sent by one member (e.g.
  ``{"action": "code", "data": "..."}``) is delivered verbatim to every *other*
  connected member; the sender does not receive its own message back.
* **Room lifecycle (in-memory)** — the first connection for a room makes it live
  in ``room_manager.rooms``; when the last connection drops, it is removed.

DB state is arranged with the async ``db`` fixture/factories; the socket I/O
goes through the synchronous ``ws_client`` (FastAPI ``TestClient``), which runs
the app in an in-process portal thread.
"""

import asyncio
import time

import pytest
from fastapi import WebSocketDisconnect

from factories import add_member, create_room, create_user
from helpers import auth_cookies, make_token

pytestmark = pytest.mark.asyncio


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def ws_url(room_id: int) -> str:
    return f"/rooms/{room_id}/ws"


def connect(ws_client, room_id: int, user):
    """Open an authenticated websocket to a room, as ``user`` would."""
    return ws_client.websocket_connect(
        ws_url(room_id), cookies=auth_cookies(user.id)
    )


def presence(user, action: str) -> dict:
    """The presence ``WSRoomAction`` broadcast when ``user`` joins/leaves.

    ``action`` is ``"connect"`` or ``"disconnect"``; ``data`` carries the user's
    public info (``User.info()``).
    """
    return {"action": action, "data": {"id": user.id, "username": user.username}}


async def recv_json(ws, *, timeout: float = 2.0):
    """Receive one JSON message, failing fast instead of hanging forever.

    ``WebSocketTestSession.receive_json`` blocks with no timeout. If the server
    never sends the expected message — e.g. a handler crashed *before*
    broadcasting, so the awaited message will never come — an unbounded receive
    would wedge the whole suite. Running it under ``wait_for`` turns that into a
    prompt, readable failure (and any server-side exception surfaced by the
    receive is re-raised here, fast, instead of racing teardown).
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(ws.receive_json), timeout)
    except asyncio.TimeoutError as exc:
        raise AssertionError(
            f"timed out after {timeout}s waiting for a websocket message "
            "(the server likely never sent it — e.g. a handler crashed before "
            "broadcasting)"
        ) from exc


async def wait_until(predicate, *, timeout: float = 2.0, interval: float = 0.02):
    """Poll ``predicate`` until true or ``timeout`` elapses.

    The websocket handler runs in the TestClient's portal thread, so state it
    mutates (``room_manager.rooms``) becomes visible to the test thread slightly
    after the triggering call returns. This avoids racy asserts without a fixed
    sleep.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return False


# --------------------------------------------------------------------------- #
# Connecting: the auth gate.
# --------------------------------------------------------------------------- #
class TestRoomWebsocketConnect:
    async def test_rejects_connection_without_cookie(self, ws_client, db):
        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        with pytest.raises(WebSocketDisconnect):
            with ws_client.websocket_connect(ws_url(room.id)):
                pass

    async def test_rejects_invalid_token(self, ws_client, db):
        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        bad = {"auth_token": make_token(owner.id, key="not-the-real-key")}
        with pytest.raises(WebSocketDisconnect):
            with ws_client.websocket_connect(ws_url(room.id), cookies=bad):
                pass

    async def test_authenticated_member_can_connect(self, ws_client, db):
        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        with connect(ws_client, room.id, owner) as ws:
            # A lone joiner gets no presence message about itself; the
            # connection simply stays open.
            assert ws is not None


# --------------------------------------------------------------------------- #
# In-memory room lifecycle: live on first join, gone on last leave.
# --------------------------------------------------------------------------- #
class TestRoomWebsocketLifecycle:
    async def test_room_is_created_on_connect_and_removed_on_disconnect(
        self, ws_client, manager, db
    ):
        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        assert room.id not in manager.rooms

        with connect(ws_client, room.id, owner):
            assert await wait_until(lambda: room.id in manager.rooms)

        # Last (only) connection dropped -> the room is torn down again.
        assert await wait_until(lambda: room.id not in manager.rooms)

    async def test_room_survives_while_a_member_remains(self, ws_client, manager, db):
        owner = await create_user(db)
        other = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=other, room=room)

        with connect(ws_client, room.id, owner) as ws_owner:
            with connect(ws_client, room.id, other):
                # Owner sees the joiner announced -> both are registered now.
                assert await recv_json(ws_owner) == presence(other, "connect")
                assert await wait_until(
                    lambda: len(manager.rooms[room.id].connections) == 2
                )

            # The second member left, but the owner is still connected, so the
            # room must NOT be deleted.
            assert await recv_json(ws_owner) == presence(other, "disconnect")
            assert await wait_until(
                lambda: room.id in manager.rooms
                and len(manager.rooms[room.id].connections) == 1
            )

        assert await wait_until(lambda: room.id not in manager.rooms)


# --------------------------------------------------------------------------- #
# Broadcast: presence + edits fan out to the *other* members only.
# --------------------------------------------------------------------------- #
class TestRoomWebsocketBroadcast:
    async def test_join_and_leave_are_announced_to_others(self, ws_client, db):
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with connect(ws_client, room.id, owner) as ws_owner:
            with connect(ws_client, room.id, joiner):
                assert await recv_json(ws_owner) == presence(joiner, "connect")
            # Closing the joiner's socket announces the departure to the owner.
            assert await recv_json(ws_owner) == presence(joiner, "disconnect")

    async def test_edit_is_broadcast_to_other_members(self, ws_client, db):
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with connect(ws_client, room.id, owner) as ws_owner:
            with connect(ws_client, room.id, joiner) as ws_joiner:
                await recv_json(ws_owner)  # drain the joiner's "connect" notice

                edit = {"action": "code", "data": "print('hello')"}
                ws_joiner.send_json(edit)
                # The other member receives the edit verbatim.
                assert await recv_json(ws_owner) == edit

    async def test_sender_does_not_receive_its_own_edit(self, ws_client, db):
        # Verifies the sender is skipped: if it weren't, the joiner's queue would
        # still hold its own first edit, and the final assertion (that it next
        # reads the owner's edit) would fail.
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with connect(ws_client, room.id, owner) as ws_owner:
            with connect(ws_client, room.id, joiner) as ws_joiner:
                await recv_json(ws_owner)  # drain "connect"

                from_joiner = {"action": "code", "data": "a = 1"}
                ws_joiner.send_json(from_joiner)
                assert await recv_json(ws_owner) == from_joiner

                from_owner = {"action": "code", "data": "b = 2"}
                ws_owner.send_json(from_owner)
                # If the joiner had received its own edit, this would read
                # ``from_joiner`` instead.
                assert await recv_json(ws_joiner) == from_owner
