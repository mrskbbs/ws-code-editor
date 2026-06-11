from typing import Iterable

from app.db.models.room import Room
from app.schemas.ws import WSRoomConnection, WSRoomAction

class WSRoom():
    connections: dict[int, WSRoomConnection] = dict()
    room: Room
    code: str
    stdin: str # TODO: add support for later on
    stdout: str
    
    def __init__(self, room) -> None:
        self.code = room.code

    async def broadcast(self, data: WSRoomAction, skip: Iterable[WSRoomConnection] | None = None):
        skip_set = None if not skip else set(conn.user.id for conn in skip)
        for conn in self.connections.values():
            if skip != None and conn.user.id in skip_set:
                continue
            await conn.ws.send_json(data.model_dump(mode="json"))

    async def connect(self, conn: WSRoomConnection):
        await self.broadcast(
            WSRoomAction(
                action="connect",
                data=conn.user.info(),
            ),
        )
        self.connections[conn.user.id] = conn

    async def disconnect(self, conn: WSRoomConnection): 
        self.connections.pop(conn.user.id)
        await self.broadcast(
            WSRoomAction(
                action="disconnect",
                data=conn.user.info(),
            ),
        )

    async def handle(self, conn: WSRoomConnection, data: WSRoomAction):
        await self.broadcast(data, skip=(conn,))
