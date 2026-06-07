"""Small, dependency-free helpers shared across tests.

Kept separate from ``factories.py`` (which writes to the DB) so that pure
request/auth helpers can be used without a database session.
"""

import jwt

from app.config import JWT_ALGO, JWT_KEY, SALT
from app.utils import sha256salt


def make_token(user_id: int, *, key: str = JWT_KEY, algo: str = JWT_ALGO) -> str:
    """Forge an auth JWT exactly like the auth router does.

    ``key``/``algo`` are overridable so tests can produce *invalid* tokens
    (e.g. signed with the wrong key) to exercise the auth failure paths.
    """
    return jwt.encode({"id": user_id}, key, algorithm=algo)


def auth_cookies(user_id: int) -> dict[str, str]:
    """Cookie dict that authenticates the given user, ready to pass to httpx.

    Usage::

        await client.get("/rooms/", cookies=auth_cookies(user.id))
    """
    return {"auth_token": make_token(user_id)}


def hash_password(password: str) -> str:
    """Hash a password the same way the app stores it, for direct DB inserts."""
    return sha256salt(password, SALT)
