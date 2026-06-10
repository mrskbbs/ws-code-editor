from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from app.db import DbDep
from app.db.models.room import Room
from app.db.models.room_members import room_members
from app.dependencies.users import UserDep

async def getRoom(room_id: int, db: DbDep):
    room = await db.get(Room, room_id)

    if not room:
        raise HTTPException(HTTP_404_NOT_FOUND)

    return room

async def isRoomMember(room_id: int, user: UserDep, db: DbDep):
    is_member = await db.scalar(select(
        select(room_members.c.room_id)
        .where(
            room_members.c.user_id == user.id,
            room_members.c.room_id == room_id,
        ).exists()
    ))

    if not is_member:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            { "message": "Forbiden" }
        )

async def isRoomOwner(room: RoomDep, user: UserDep):
    if room.owner_id != user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            { "message": "Forbiden" }
        )

RoomDep = Annotated[Room, Depends(getRoom)]
