import uuid
from flask import Request, session
from flask_socketio import emit, join_room, leave_room
from app.db import injectDb
from app.models.room import RoomDynamicModel
from app.models.user import UserModelNew
from app.services.auth import AuthService
from app.services.room import RoomService
from app.utils import logger
from sqlalchemy.orm import Session

class RoomWSController():
    request: Request
    rooms: dict[uuid.UUID, RoomDynamicModel]
    room: RoomDynamicModel
    user: UserModelNew

    @injectDb
    def __init__(self, request: Request, rooms: dict[uuid.UUID, RoomDynamicModel], db: Session):
        self.request = request
        self.rooms = rooms
        self.user = session["user"]
        
    
    def __formatListToJson__(self, arr) -> dict:
        if type(arr) is not list:
            raise TypeError("Inappropriate type for __formatListToJson__")
        
        d = dict()
        
        for i in range(len(arr)):
            d[i] = arr[i]

        return d


    def __formatConnections__(self) -> list[dict]:
        return [user.to_dict(only=("id", "username")) for user in self.room.connections]


    def __sendError__(self, text: list[str], exc: Exception):
        logger.error(exc)
        # TODO: Depending on value of production ON/OFF this traceback
        full_text = text + [repr(exc)]
        self.room.setStderr(full_text)
        emit("stderr", self.room.stderr, to=self.room.id)


    def connect(self):
        room_id = uuid.UUID(self.request.args.get("room_id"))
        room = self.rooms.get(room_id) 
        try:
            if room == None:
                room_db = RoomService().get(room_id)
                self.rooms[room_id] = RoomDynamicModel(room_db)
                self.room = self.rooms[room_id]
            else:
                self.room = room

        except Exception:
            raise Exception("Room does not exist")
        
        if self.user in self.room.connections:
            raise Exception("You are already present in this room from another device")
        
        join_room(room=str(self.room.id), sid=str(self.user.id))
        self.room.connections.add(self.user)

        emit("code", self.__formatListToJson__(self.room.code), to=str(self.user.id))
        emit("stdin", self.__formatListToJson__(self.room.stdin), to=str(self.user.id))
        emit("stdout", self.room.stdout, to=str(self.user.id))
        emit(
            "connections", 
            self.__formatConnections__(), 
            to=self.room.id
        )


    def disconnect(self):
        leave_room(room=str(self.room.id), sid=str(self.user.id))
        self.room.connections.remove(self.user)

        emit(
            "connections", 
            self.__formatConnections__(), 
            to=self.room.id
        )

        if len(self.room.connections) == 0:
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
                self.room.code_location[self.user.id] = location
            else: 
                self.room.code_location.pop(self.user.id, None)
            emit("code_location", {
                "location": location,
                "user": str(self.user.id),
            }, to=self.room.id, include_self=False)
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change code location:"], exc)

    def locationStdin(self, location: list[int]):
        try:
            if len(location) > 0: 
                self.room.stdin_location[self.user.id] = location
            else: 
                self.room.stdin_location.pop(self.user.id, None)
            emit("stdin_location", {
                "location": location,
                "user": str(self.user.id),
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