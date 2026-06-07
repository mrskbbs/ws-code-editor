"""Behavioural tests for the /rooms router (HTTP only; the websocket route is
covered separately under ``tests/ws/``).

The whole router sits behind auth, so every endpoint has a "no auth -> 401"
test. Endpoints that are currently stubs (``editRoom`` does not yet apply the
payload; ``deleteRoom`` is a no-op) are described with ``xfail`` so they turn
green the moment they're implemented.
"""

import pytest
from sqlalchemy import func, select

from app.db.models.room import Room
from app.db.models.room_members import room_members_association_table as room_members

from factories import add_member, create_language, create_room, create_user
from helpers import auth_cookies

pytestmark = pytest.mark.asyncio


# --------------------------------------------------------------------------- #
# Auth boundary: every route rejects unauthenticated callers.
# --------------------------------------------------------------------------- #
class TestRequiresAuth:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("GET", "/rooms/"),
            ("POST", "/rooms/"),
            ("GET", "/rooms/1"),
            ("PUT", "/rooms/1"),
            ("DELETE", "/rooms/1"),
            ("GET", "/rooms/invite/some-token"),
        ],
    )
    async def test_unauthenticated_is_rejected(self, client, method, path):
        res = await client.request(method, path)
        assert res.status_code == 401


# --------------------------------------------------------------------------- #
# GET /rooms/  (rooms the current user belongs to)
# --------------------------------------------------------------------------- #
class TestListRooms:
    async def test_empty_when_user_has_no_rooms(self, client, db):
        user = await create_user(db)

        res = await client.get("/rooms/", cookies=auth_cookies(user.id))

        assert res.status_code == 200
        assert res.json() == []

    async def test_lists_rooms_the_user_is_member_of(self, client, db):
        user = await create_user(db)
        room = await create_room(db, owner=user, title="my room")

        res = await client.get("/rooms/", cookies=auth_cookies(user.id))

        assert res.status_code == 200
        returned_ids = [r["id"] for r in res.json()]
        assert room.id in returned_ids

    async def test_does_not_list_other_peoples_rooms(self, client, db):
        owner = await create_user(db)
        other = await create_user(db)
        await create_room(db, owner=owner)

        res = await client.get("/rooms/", cookies=auth_cookies(other.id))

        assert res.status_code == 200
        assert res.json() == []


# --------------------------------------------------------------------------- #
# POST /rooms/  (create a room)
# --------------------------------------------------------------------------- #
class TestCreateRoom:
    async def test_creates_room_owned_by_caller(self, client, db):
        user = await create_user(db)
        language = await create_language(db)

        res = await client.post(
            "/rooms/",
            json={"title": "Project X", "language_id": language.id},
            cookies=auth_cookies(user.id),
        )

        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "Project X"
        assert body["owner_id"] == user.id
        assert body["language_id"] == language.id
        # New rooms start with empty code and get a generated invite token.
        assert body["code"] == ""
        assert body["invite_token"]

        # Persisted in the database.
        room = await db.scalar(select(Room).where(Room.id == body["id"]))
        assert room is not None
        assert room.title == "Project X"

    async def test_missing_fields_is_validation_error(self, client, db):
        user = await create_user(db)

        res = await client.post(
            "/rooms/",
            json={"title": "no language"},
            cookies=auth_cookies(user.id),
        )

        assert res.status_code == 422


# --------------------------------------------------------------------------- #
# GET /rooms/invite/{invite_token}  (join via invite link)
# --------------------------------------------------------------------------- #
class TestRoomInvite:
    async def test_valid_token_adds_membership(self, client, db):
        owner = await create_user(db)
        joiner = await create_user(db)
        room = await create_room(db, owner=owner)

        res = await client.get(
            f"/rooms/invite/{room.invite_token}",
            cookies=auth_cookies(joiner.id),
        )

        assert res.status_code == 200
        # The joiner is now a member of the room.
        is_member = await db.scalar(
            select(
                select(room_members.c.room_id)
                .where(
                    room_members.c.user_id == joiner.id,
                    room_members.c.room_id == room.id,
                )
                .exists()
            )
        )
        assert is_member is True

    async def test_invalid_token_is_not_found(self, client, db):
        user = await create_user(db)

        res = await client.get(
            "/rooms/invite/does-not-exist",
            cookies=auth_cookies(user.id),
        )

        assert res.status_code == 404


# --------------------------------------------------------------------------- #
# GET /rooms/{id}  (fetch a single room)
# --------------------------------------------------------------------------- #
class TestGetRoom:
    async def test_member_can_read_room(self, client, db):
        user = await create_user(db)
        room = await create_room(db, owner=user, title="readable")

        res = await client.get(f"/rooms/{room.id}", cookies=auth_cookies(user.id))

        assert res.status_code == 200
        body = res.json()
        assert body["id"] == room.id
        assert body["title"] == "readable"

    async def test_non_member_is_forbidden(self, client, db):
        owner = await create_user(db)
        outsider = await create_user(db)
        room = await create_room(db, owner=owner)

        res = await client.get(
            f"/rooms/{room.id}", cookies=auth_cookies(outsider.id)
        )

        assert res.status_code == 403


# --------------------------------------------------------------------------- #
# PUT /rooms/{id}  (edit a room)
# --------------------------------------------------------------------------- #
class TestEditRoom:
    @pytest.mark.xfail(
        reason="editRoom does not yet apply the request payload",
        strict=False,
    )
    async def test_updates_title(self, client, db):
        user = await create_user(db)
        room = await create_room(db, owner=user, title="old title")

        res = await client.put(
            f"/rooms/{room.id}",
            json={"title": "new title"},
            cookies=auth_cookies(user.id),
        )

        assert res.status_code == 200
        assert res.json()["title"] == "new title"

        refreshed = await db.scalar(select(Room).where(Room.id == room.id))
        assert refreshed is not None
        assert refreshed.title == "new title"


# --------------------------------------------------------------------------- #
# DELETE /rooms/{id}  (delete a room)
# --------------------------------------------------------------------------- #
class TestDeleteRoom:
    @pytest.mark.xfail(reason="deleteRoom is not implemented yet", strict=False)
    async def test_deletes_room(self, client, db):
        user = await create_user(db)
        room = await create_room(db, owner=user)

        res = await client.delete(
            f"/rooms/{room.id}", cookies=auth_cookies(user.id)
        )

        assert res.status_code in (200, 204)

        remaining = await db.scalar(
            select(func.count()).select_from(Room).where(Room.id == room.id)
        )
        assert remaining == 0
