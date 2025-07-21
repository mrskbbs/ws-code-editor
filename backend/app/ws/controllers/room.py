import uuid
from flask import Request, session
from flask_socketio import disconnect, emit, join_room, leave_room
from sqlalchemy import update
from app.db import injectDb
from app.models.room import RoomDynamicModel, RoomModelNew
from app.models.user import UserModelNew
from app.services.auth import AuthService
from app.services.room import RoomService
from app.types.auth import AuthSessionInfo, HashableAuthSessionInfo
from app.utils import logger
from sqlalchemy.orm import Session

class RoomWSController():
    request: Request
    rooms: dict[uuid.UUID, RoomDynamicModel]
    room: RoomDynamicModel = None
    user: AuthSessionInfo

    def __init__(self, request: Request, rooms: dict[uuid.UUID, RoomDynamicModel]):
        self.request = request
        self.rooms = rooms
        self.user = session["user"]

        self.room_id = uuid.UUID(self.request.args.get("room_id"))
        self.room = self.rooms.get(self.room_id)
        
    
    def __formatListToJson__(self, arr) -> dict:
        if type(arr) is not list:
            raise TypeError("Inappropriate type for __formatListToJson__")
        
        d = dict()
        
        for i in range(len(arr)):
            d[i] = arr[i]

        return d


    def __formatConnections__(self) -> list[dict]:
        return [user.full for user in self.room.connections]


    def __sendError__(self, text: list[str], exc: Exception):
        logger.error(exc)
        # TODO: Depending on value of production ON/OFF this traceback
        full_text = text + [repr(exc)]
        self.room.setStderr(full_text)
        emit("stderr", self.room.stderr, to=self.room.id)


    def connect(self):
        try:
            if self.user == None:
                raise Exception("You are not authorized")
            if self.room_id == None:
                raise Exception("No room id is provided")


            if self.room_id in self.rooms:
                self.room = self.rooms.get(self.room_id)
            else: 
                room_db: RoomModelNew = RoomService().get(self.room_id)
                room = RoomDynamicModel(room_db)
                self.rooms[self.room_id] = room
                self.room = room

        except Exception:
            disconnect()
            raise Exception("Room does not exist")
        
        if self.user["id"] in self.room.connections:
            disconnect()
            raise Exception("You are already present in this room from another device")
        
        join_room(room=str(self.room.id), sid=self.request.sid)
        self.room.connections.add(HashableAuthSessionInfo(self.user))
        emit("init", {
            "name": self.room.name,
            "invite_token": self.room.invite_token
        })
        emit("code", self.__formatListToJson__(self.room.code), to=self.request.sid)
        emit("stdin", self.__formatListToJson__(self.room.stdin), to=self.request.sid)
        emit("stdout", self.room.stdout, to=self.request.sid)
        emit(
            "connections", 
            self.__formatConnections__(), 
            to=self.room.id
        )


    @injectDb
    def disconnect(self, db: Session):
        leave_room(room=str(self.room.id), sid=self.request.sid)
        self.room.connections.remove(HashableAuthSessionInfo(self.user))

        emit(
            "connections", 
            self.__formatConnections__(), 
            to=self.room.id
        )

        if len(self.room.connections) == 0:
            try:
                update(RoomModelNew).values(
                    code="\n".join(self.room.code),
                    stdin="\n".join(self.room.stdin),
                ).where(
                    id=self.room.id
                )
                db.commit()
                
            except: 
                logger.warning(f"Failed to save state for room #{self.room.id}")
                db.rollback()

            self.rooms.pop(self.room.id, None)

    def setCode(self, diffs: dict[int, str | None]):
        try:
            self.room.setCode(diffs)
            emit("code", diffs, to=self.room.id, include_self=False)
            logger.debug(f"[CODE]@[{self.room.id}] {repr(self.room.code)}")
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change the code:"], exc)

    def setStdin(self, diffs: dict[int, str | None]):
        try:
            self.room.setStdin(diffs)
            emit("stdin", diffs, to=self.room.id, include_self=False)
            logger.debug(f"[STDIN]@[{self.room.id}] {repr(self.room.stdin)}")
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change the stdin:"], exc)
    
    def locationCode(self, location: list[int]):
        try:
            if len(location) > 0: 
                self.room.code_location[self.user["id"]] = location
            else: 
                self.room.code_location.pop(self.user["id"], None)
            emit("code_location", {
                "location": location,
                "user": str(self.user["id"]),
            }, to=self.room.id, include_self=False)
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change code location:"], exc)

    def locationStdin(self, location: list[int]):
        try:
            if len(location) > 0: 
                self.room.stdin_location[self.user["id"]] = location
            else: 
                self.room.stdin_location.pop(self.user["id"], None)
            emit("stdin_location", {
                "location": location,
                "user": str(self.user["id"]),
            }, to=self.room.id, include_self=False)
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change stdin location:"], exc)

    def run(self):
        try:
            emit("run", True, to=self.room.id)
            stdout, stderr = self.room.run()
            emit("run", False, to=self.room.id)

            emit("stdout", stdout, to=self.room.id)
            emit("stderr", stderr, to=self.room.id)
            
            logger.debug(f"[STDOUT]@[{self.room.id}] {repr(self.room.stdout)}")
            logger.debug(f"[STDERR]@[{self.room.id}] {repr(self.room.stderr)}")
        
        except Exception as exc:
            self.__sendError__(["Error occured while trying to run the script:"], exc)
            emit("run", False, to=self.room.id)