from typing import Any, Iterable

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

    async def broadcast(self, data: Any, skip: Iterable[int] | None = None):
        skip_set = None if not skip else set(skip)
        for conn in self.connections.values():
            if skip_set and conn.user.id in skip_set:
                continue
            await conn.ws.send_json(data)

    async def connect(self, conn: WSRoomConnection):
        await self.broadcast({"connected": conn.user})
        self.connections[conn.user.id] = conn

    async def disconnect(self, conn: WSRoomConnection): 
        await self.broadcast({"disconnected": conn.user})
        self.connections.pop(conn.user.id)

    async def handle(self, conn: WSRoomConnection, data: WSRoomAction):
        await self.broadcast(data, skip=(conn.user.id,))
