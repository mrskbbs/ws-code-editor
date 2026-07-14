from typing import Iterable, Literal
from fastapi import WebSocketException, status
from pycrdt import Doc, Text
from httpx import AsyncClient, TimeoutException

from app.config import CODE_TIMEOUT, SANDBOX_URL
from app.db.models.room import Room
from app.schemas.ws import WSRoomConnection, WSRoomAction

class WSRoom():
    connections: dict[int, WSRoomConnection] = dict()
    room: Room
    code_doc: Doc
    code_text: Text
    # stdin_text: Text # TODO: add support for later on
    stdout: str
    is_running: bool = False
    
    def __init__(self, room: Room) -> None:
        self.room = room
        self.code_doc = Doc()
        self.code_text = Text(room.code) # get code from db
        self.code_doc["content"] = self.code_text

    async def handle(self, conn: WSRoomConnection, msg: WSRoomAction):
        try:
            match msg.action:
                case "run_code":
                    await self.runCode()
                case "update_code":
                    await self.updateCode(msg.payload)
                case "connect":
                    await self.connect(conn)
                case "disconnect":
                    await self.disconnect(conn)
                case _:
                    raise WebSocketException(status.WS_1011_INTERNAL_ERROR, "Invalid action")
        except WebSocketException as e:
            raise e
        except Exception as e:
            raise WebSocketException(status.WS_1011_INTERNAL_ERROR, "Internal error")
            

    async def broadcast(self, msg: WSRoomAction, skip: Iterable[WSRoomConnection] | None = None,  payload_type: Literal["json", "bytes"] = "json"):
        skip_set = None if not skip else set(conn.user.id for conn in skip)
        for conn in self.connections.values():
            if skip != None and conn.user.id in skip_set:
                continue
            match payload_type:
                case "bytes":
                    await conn.ws.send_bytes(msg.payload)
                case "json":
                    await conn.ws.send_json(msg.model_dump(mode="json"))

    async def connect(self, conn: WSRoomConnection):
        await self.broadcast(
            WSRoomAction(
                action="connect",
                payload=conn.user.info(),
            ),
        )
        self.connections[conn.user.id] = conn

    async def disconnect(self, conn: WSRoomConnection): 
        self.connections.pop(conn.user.id)

        if len(self.connections) == 0:
            # save room state
            return 

        await self.broadcast(
            WSRoomAction(
                action="disconnect",
                payload=conn.user.info(),
            ),
        )

    async def updateCode(self, update: bytes):
        self.code_doc.apply_update(update)

        await self.broadcast(
            WSRoomAction(
                action="update_code",
                payload=update,
            ),
        )
        
    async def runCode(self):
        if self.is_running:
            return

        self.is_running = True
        async with AsyncClient(timeout=CODE_TIMEOUT) as client:
            try: 
                res = await client.request(
                    "POST", 
                    f"{SANDBOX_URL}/{self.room.language.ext}/exec", 
                    json={
                        "code": self.code_text.to_py(),
                    },
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                await self.broadcast(
                    WSRoomAction(
                        action="output",
                        payload=res.json(),
                    )
                )
            except TimeoutException:
                await self.broadcast(
                    WSRoomAction(
                        action="output",
                        payload={
                            "stdout": "",
                            "stderr": "Code execution timed out"
                        },
                    )
                )
            finally:
                self.is_running = False

