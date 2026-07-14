"""Async data factories: create domain objects directly in the test database.

These bypass the HTTP layer on purpose. Use them to *arrange* the state a test
needs (a user that already exists, a room someone owns, an existing membership)
so the test body can focus on the one behaviour under test.

Every factory takes an ``AsyncSession`` as its first argument (use the ``db``
fixture) and commits before returning, so the created rows are visible to the
request handlers running against the same database.
"""

import uuid

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.language import Language
from app.db.models.room import Room
from app.db.models.room_members import room_members
from app.db.models.user import User

from helpers import hash_password

# Monotonic counters keep factory-created rows unique without every caller
# having to invent distinct usernames / titles.
_counter = {"user": 0, "language": 0, "room": 0}


def _next(kind: str) -> int:
    _counter[kind] += 1
    return _counter[kind]


async def create_user(
    db: AsyncSession,
    *,
    username: str | None = None,
    password: str = "password",
) -> User:
    """Create and persist a user. Returns the refreshed ORM object."""
    n = _next("user")
    user = User(
        username=username or f"user{n}",
        password=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_language(
    db: AsyncSession,
    *,
    name: str | None = None,
    ext: str | None = None,
) -> Language:
    """Create and persist a language (rooms require a valid ``language_id``)."""
    n = _next("language")
    language = Language(
        name=name or f"lang{n}",
        ext=ext or f"lang{n}",
    )
    db.add(language)
    await db.commit()
    await db.refresh(language)
    return language


async def create_room(
    db: AsyncSession,
    *,
    owner: User,
    language: Language | None = None,
    title: str | None = None,
    code: str = "",
    add_owner_as_member: bool = True,
) -> Room:
    """Create and persist a room owned by ``owner``.

    If ``language`` is omitted a fresh one is created. By default the owner is
    also added to the room's member list (matching the expectation that an owner
    can access their own room).
    """
    if language is None:
        language = await create_language(db)

    n = _next("room")
    room = Room(
        title=title or f"room{n}",
        code=code,
        invite_token=str(uuid.uuid4()),
        owner_id=owner.id,
        language_id=language.id,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    if add_owner_as_member:
        await add_member(db, user=owner, room=room)

    return room


async def add_member(db: AsyncSession, *, user: User, room: Room) -> None:
    """Add ``user`` to ``room``'s membership table."""
    await db.execute(
        insert(room_members).values(user_id=user.id, room_id=room.id)
    )
    await db.commit()
