"""Groundwork for the collaborative-room websocket (``/rooms/{id}/ws``).

The endpoint isn't implemented yet, so this whole module is skipped. It exists
to (a) lock in the *expected* behaviour as executable documentation and (b) give
the next person a ready-made harness — just delete the ``pytestmark`` skip (and
fill in the message shapes) once the route lands.

Expected behaviour, as currently understood:
  * Connecting requires authentication (a valid ``auth_token`` cookie).
  * Connecting requires the user to be a member of the room (non-members are
    rejected / the socket is closed).
  * A code edit sent by one member is broadcast to the other connected members.
  * The latest code is persisted to ``Room.code`` so late joiners catch up.

These are async tests because they arrange DB state with the async ``db``
fixture; the actual socket I/O goes through the synchronous ``ws_client``.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="websocket route /rooms/{id}/ws not implemented yet"
)


class TestRoomWebsocketAuth:
    def test_rejects_connection_without_cookie(self, ws_client, db):
        # with pytest.raises(WebSocketDisconnect):
        #     with ws_client.websocket_connect("/rooms/1/ws"):
        #         pass
        ...

    def test_rejects_non_member(self, ws_client, db):
        # owner = await create_user(db); outsider = await create_user(db)
        # room = await create_room(db, owner=owner)
        # with pytest.raises(WebSocketDisconnect):
        #     ws_client.websocket_connect(
        #         f"/rooms/{room.id}/ws", cookies=auth_cookies(outsider.id)
        #     ).__enter__()
        ...


class TestRoomWebsocketBroadcast:
    def test_edit_is_broadcast_to_other_members(self, ws_client, db):
        # Two members connect; an edit from one is received by the other.
        ...

    def test_latest_code_is_persisted_for_late_joiners(self, ws_client, db):
        # After an edit, a freshly connecting member receives the current code,
        # and Room.code reflects the last edit in the database.
        ...
