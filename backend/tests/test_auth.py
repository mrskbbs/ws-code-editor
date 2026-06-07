"""Behavioural tests for the /auth router.

Each test states what the endpoint is *expected* to do. Where the current
implementation is known to be incomplete the test still describes the target
behaviour (marked ``xfail`` so it flips to passing once implemented, rather than
red-failing the suite forever).
"""

import pytest
from sqlalchemy import func, select

from app.db.models.user import User

from factories import create_user
from helpers import auth_cookies, hash_password, make_token

pytestmark = pytest.mark.asyncio


# --------------------------------------------------------------------------- #
# POST /auth/signup
# --------------------------------------------------------------------------- #
class TestSignup:
    async def test_creates_user_and_returns_identity(self, client, db):
        res = await client.post(
            "/auth/signup",
            json={"username": "alice", "password": "s3cret"},
        )

        assert res.status_code == 200
        body = res.json()
        assert body["username"] == "alice"
        assert "id" in body
        # Password must never be echoed back.
        assert "password" not in body

        # The user is actually persisted...
        user = await db.scalar(select(User).where(User.username == "alice"))
        assert user is not None
        # ...with the password stored hashed, not in plaintext.
        assert user.password == hash_password("s3cret")
        assert user.password != "s3cret"

    async def test_sets_auth_cookie(self, client):
        res = await client.post(
            "/auth/signup",
            json={"username": "bob", "password": "pw"},
        )

        assert res.status_code == 200
        assert "auth_token" in res.cookies

    async def test_duplicate_username_is_rejected(self, client, db):
        await create_user(db, username="dupe")

        res = await client.post(
            "/auth/signup",
            json={"username": "dupe", "password": "pw"},
        )

        assert res.status_code >= 400
        # Still exactly one "dupe" in the database.
        count = await db.scalar(
            select(func.count()).select_from(User).where(User.username == "dupe")
        )
        assert count == 1

    async def test_missing_fields_is_validation_error(self, client):
        res = await client.post("/auth/signup", json={"username": "no_pw"})
        assert res.status_code == 422


# --------------------------------------------------------------------------- #
# POST /auth/login
# --------------------------------------------------------------------------- #
class TestLogin:
    async def test_valid_credentials_succeed(self, client, db):
        await create_user(db, username="carol", password="hunter2")

        res = await client.post(
            "/auth/login",
            json={"username": "carol", "password": "hunter2"},
        )

        assert res.status_code == 200
        body = res.json()
        assert body["username"] == "carol"
        assert "id" in body
        assert "auth_token" in res.cookies

    async def test_wrong_password_is_unauthorized(self, client, db):
        await create_user(db, username="dave", password="correct")

        res = await client.post(
            "/auth/login",
            json={"username": "dave", "password": "wrong"},
        )

        assert res.status_code == 401

    async def test_unknown_user_is_unauthorized(self, client):
        res = await client.post(
            "/auth/login",
            json={"username": "ghost", "password": "whatever"},
        )

        assert res.status_code == 401

    async def test_missing_fields_is_validation_error(self, client):
        res = await client.post("/auth/login", json={"username": "x"})
        assert res.status_code == 422


# --------------------------------------------------------------------------- #
# GET /auth/  (current identity)
# --------------------------------------------------------------------------- #
class TestGetAuth:
    async def test_returns_current_user_when_authenticated(self, client, db):
        user = await create_user(db, username="erin")

        res = await client.get("/auth/", cookies=auth_cookies(user.id))

        assert res.status_code == 200
        body = res.json()
        assert body == {"id": user.id, "username": "erin"}

    async def test_without_cookie_is_unauthorized(self, client):
        res = await client.get("/auth/")
        assert res.status_code == 401

    async def test_with_invalid_token_is_unauthorized(self, client, db):
        user = await create_user(db, username="frank")
        # Token signed with the wrong key must not be accepted.
        bad = make_token(user.id, key="not-the-real-key")

        res = await client.get("/auth/", cookies={"auth_token": bad})

        assert res.status_code == 401

    async def test_token_for_missing_user_is_unauthorized(self, client):
        # Well-formed token, but no such user in the database.
        res = await client.get("/auth/", cookies=auth_cookies(999999))
        assert res.status_code == 401


# --------------------------------------------------------------------------- #
# POST /auth/logout
# --------------------------------------------------------------------------- #
class TestLogout:
    async def test_logout_when_authenticated(self, client, db):
        user = await create_user(db, username="grace")

        res = await client.post("/auth/logout", cookies=auth_cookies(user.id))

        assert res.status_code == 200
        assert res.json() == {"message": "Logged out"}

    async def test_logout_without_cookie_is_unauthorized(self, client):
        res = await client.post("/auth/logout")
        assert res.status_code == 401
