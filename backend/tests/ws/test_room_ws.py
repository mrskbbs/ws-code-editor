"""Behavioural tests for the collaborative-room websocket (``/rooms/{id}/ws``).

These tests describe the *expected* work cycle of the endpoint — they are the
contract the route is meant to satisfy, not a description of the current
implementation. Run them with::

    pytest tests/ws/

Expected protocol
-----------------
A client opens a websocket to ``/rooms/{id}/ws`` authenticated by the same
``auth_token`` cookie used by the HTTP routes. Once connected:

* **Auth gate** — a connection with no / an invalid ``auth_token`` cookie is
  rejected (the handshake fails and the socket closes).
* **Membership gate** — an authenticated user who is *not* a member of the room
  is rejected.
* **Presence (broadcast)** — when a member joins, the members already connected
  receive ``{"connected": {"id": .., "username": ..}}``; when a member leaves,
  the rest receive ``{"disconnected": {"id": .., "username": ..}}``. A joiner
  does not receive a presence message about itself.
* **Edit broadcast** — a JSON action sent by one member (e.g.
  ``{"action": "code", "code": "..."}``) is delivered verbatim to every *other*
  connected member; the sender does not receive its own message back.
* **Room lifecycle (in-memory)** — the first connection for a room registers a
  live room in ``room_manager``; when the last connection drops, that room is
  removed again.

These are ``async`` tests so DB state can be arranged with the async ``db``
fixture/factories; the socket I/O itself goes through the synchronous
``ws_client`` (FastAPI ``TestClient``), which runs the app in an in-process
portal thread.
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


async def wait_until(predicate, *, timeout: float = 2.0, interval: float = 0.02):
    """Poll ``predicate`` until true or ``timeout`` elapses.

    The websocket handler runs in the TestClient's portal thread, so state it
    mutates (e.g. ``room_manager.rooms``) becomes visible to the test thread
    slightly after the call that triggered it returns. This avoids racy asserts
    without hard-coding a sleep.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return False


def expected_presence(user) -> dict:
    return {"id": user.id, "username": user.username}


# --------------------------------------------------------------------------- #
# Connecting: auth + membership gate
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

    async def test_rejects_non_member(self, ws_client, db):
        owner = await create_user(db)
        outsider = await create_user(db)
        room = await create_room(db, owner=owner)

        with pytest.raises(WebSocketDisconnect):
            with ws_client.websocket_connect(
                ws_url(room.id), cookies=auth_cookies(outsider.id)
            ):
                pass

    async def test_member_can_connect(self, ws_client, db):
        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ) as ws:
            # A lone joiner gets no presence message about itself; the
            # connection simply stays open.
            assert ws is not None


# --------------------------------------------------------------------------- #
# In-memory room lifecycle: created on first join, deleted on last leave.
# --------------------------------------------------------------------------- #
class TestRoomWebsocketLifecycle:
    async def test_room_created_on_connect_and_deleted_on_disconnect(
        self, ws_client, db
    ):
        from app.ws.room_manager import room_manager

        owner = await create_user(db)
        room = await create_room(db, owner=owner)

        assert room.id not in room_manager.rooms

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ):
            assert await wait_until(lambda: room.id in room_manager.rooms)

        # Last (only) connection dropped -> the room is torn down again.
        assert await wait_until(lambda: room.id not in room_manager.rooms)

    async def test_room_survives_while_a_member_remains(self, ws_client, db):
        from app.ws.room_manager import room_manager

        owner = await create_user(db)
        other = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=other, room=room)

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ) as ws_owner:
            with ws_client.websocket_connect(
                ws_url(room.id), cookies=auth_cookies(other.id)
            ):
                # owner sees the joiner announced -> both are now registered.
                assert ws_owner.receive_json() == {
                    "connected": expected_presence(other)
                }
                assert await wait_until(
                    lambda: len(room_manager.rooms[room.id].connections) == 2
                )

            # The second member left, but the owner is still connected, so the
            # room must NOT be deleted.
            assert ws_owner.receive_json() == {
                "disconnected": expected_presence(other)
            }
            assert await wait_until(
                lambda: room.id in room_manager.rooms
                and len(room_manager.rooms[room.id].connections) == 1
            )

        assert await wait_until(lambda: room.id not in room_manager.rooms)


# --------------------------------------------------------------------------- #
# Broadcast: presence + edits fan out to the other members only.
# --------------------------------------------------------------------------- #
class TestRoomWebsocketBroadcast:
    async def test_join_and_leave_are_announced_to_others(self, ws_client, db):
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ) as ws_owner:
            with ws_client.websocket_connect(
                ws_url(room.id), cookies=auth_cookies(joiner.id)
            ):
                assert ws_owner.receive_json() == {
                    "connected": expected_presence(joiner)
                }
            # Closing the joiner's socket announces the departure to the owner.
            assert ws_owner.receive_json() == {
                "disconnected": expected_presence(joiner)
            }

    async def test_edit_is_broadcast_to_other_members(self, ws_client, db):
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ) as ws_owner:
            with ws_client.websocket_connect(
                ws_url(room.id), cookies=auth_cookies(joiner.id)
            ) as ws_joiner:
                # Drain the owner's presence notice for the joiner.
                assert ws_owner.receive_json() == {
                    "connected": expected_presence(joiner)
                }

                edit = {"action": "code", "code": "print('hello')"}
                ws_joiner.send_json(edit)

                # The other member receives the edit verbatim.
                assert ws_owner.receive_json() == edit

    async def test_sender_does_not_receive_its_own_edit(self, ws_client, db):
        # Verifies the sender is skipped: if it weren't, the joiner's queue would
        # still hold its own first edit, and the assertion below (that it next
        # reads the owner's edit) would fail.
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)
        await add_member(db, user=joiner, room=room)

        with ws_client.websocket_connect(
            ws_url(room.id), cookies=auth_cookies(owner.id)
        ) as ws_owner:
            with ws_client.websocket_connect(
                ws_url(room.id), cookies=auth_cookies(joiner.id)
            ) as ws_joiner:
                ws_owner.receive_json()  # drain "connected"

                from_joiner = {"action": "code", "code": "a = 1"}
                ws_joiner.send_json(from_joiner)
                assert ws_owner.receive_json() == from_joiner

                from_owner = {"action": "code", "code": "b = 2"}
                ws_owner.send_json(from_owner)
                # If the joiner had received its own edit, this would read
                # ``from_joiner`` instead.
                assert ws_joiner.receive_json() == from_owner
