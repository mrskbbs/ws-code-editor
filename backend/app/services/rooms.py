from uuid import uuid4

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import insert, select

from app.db import DbDep
from app.db.models.room import Room
from app.db.models.room_members import room_members
from app.db.models.user import User
from app.services.base import *
from app.schemas.rooms import RoomCreate, RoomEdit

async def getRoomService(req: Request, res: Response, db: DbDep): 
    return RoomService(req, res, db)

class RoomService(BaseService):

    @handleErrors
    async def getRooms(self, user: User):
        await self.db.refresh(user, ["rooms"])

        return user.rooms

    @handleErrors
    async def createRoom(self, data: RoomCreate, user: User):
        room = Room(
            title=data.title,
            invite_token=str(uuid4()),
            owner_id=user.id,
            language_id=data.language_id,
        )

        self.db.add(room)
        await self.db.flush()

        await self.db.execute(
            insert(room_members)
            .values(
                user_id=user.id,
                room_id=room.id,
            )
        )

        await self.db.commit()
        await self.db.refresh(room, ["members", "owner", "language"])

        return room

    @handleErrors
    async def roomInvite(self, invite_token: str, user: User):
        room = (await self.db.execute(
            select(Room.id)
            .where(Room.invite_token == invite_token)
        )).one_or_none()
        
        if not room:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                { "message": "Invalid invite link" }
            )

        await self.db.execute(
            insert(room_members)
            .values(
                user_id=user.id,
                room_id=room.id,
            )
        )

        await self.db.commit()

        return { "message": f"Succesfully joined the room {room.id}" }

    @handleErrors
    async def getRoom(self, room: Room):
        await self.db.refresh(room, ["members", "language", "owner"])

        return room

    @handleErrors
    async def editRoom(self, data: RoomEdit, room: Room):
        if data.title: room.title = data.title
        if data.language_id: room.language_id = data.language_id
        
        await self.db.commit()
        await self.db.refresh(room, ["members", "language", "owner"])

        return room

    @handleErrors
    async def deleteRoom(self, room: Room):
        await self.db.delete(room)
        await self.db.commit()

        return { "message": "Succesfully deleted a room" }


