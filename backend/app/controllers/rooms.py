from flask import Request
from flask_socketio import emit, join_room, leave_room
from app.model.room import RoomModel
from app.model.user import UserModel
from app.utils import logger

class RoomController():
    request: Request
    rooms: dict[str, RoomModel]
    room: RoomModel
    user: UserModel

    def __init__(self, request: Request, rooms: dict[str, RoomModel]):
        self.request = request
        self.user = UserModel(self.request)

        self.rooms = rooms
        # TODO: not that secure, room creation and join can be improved
        room_code = request.args.get("room_code")
        room = self.rooms.get(room_code) 
        if room == None:
            self.rooms[room_code] = RoomModel(room_code)
            self.room = self.rooms[room_code]
        else:
            self.room = room
    
    def __formatListToJson__(self, arr) -> dict:
        if type(arr) is not list:
            raise TypeError("Inappropriate type for __formatListToJson__")
        
        d = dict()
        
        for i in range(len(arr)):
            d[i] = arr[i]

        return d

    def __sendError__(self, text: list[str], exc: Exception):
        logger.error(exc)
        # TODO: Depending on value of production ON/OFF this traceback
        full_text = text + [repr(exc)]
        self.room.setStderr(full_text)
        emit("stderr", self.room.stderr, to=self.room.room_code)

    def connect(self):
        join_room(room=self.room.room_code, sid=self.user.sid)
        self.room.connections.add(self.user)
        emit("code", self.__formatListToJson__(self.room.code), to=self.user.sid)
        emit("stdin", self.__formatListToJson__(self.room.stdin), to=self.user.sid)
        emit("stdout", self.room.stdout, to=self.user.sid)
        emit(
            "connections", 
            list(map(str, self.room.connections)), 
            to=self.room.room_code
        )

    def disconnect(self):
        leave_room(room=self.room.room_code, sid=self.user.sid)
        self.room.connections.remove(self.user)

        emit(
            "connections", 
            list(map(str, self.room.connections)), 
            to=self.room.room_code
        )

        if len(self.room.connections) == 0:
            self.rooms.pop(self.room.room_code, None)

    def setCode(self, diffs: dict[int, str | None]):
        try:
            self.room.setCode(diffs)
            emit("code", diffs, to=self.room.room_code, include_self=False)
            logger.debug(f"[CODE]@[{self.room.room_code}] {repr(self.room.code)}")
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change the code:"], exc)

    def setStdin(self, diffs: dict[int, str | None]):
        try:
            self.room.setStdin(diffs)
            emit("stdin", diffs, to=self.room.room_code, include_self=False)
            logger.debug(f"[STDIN]@[{self.room.room_code}] {repr(self.room.stdin)}")
        except Exception as exc:
            self.__sendError__(["Error occured while trying to change the stdin:"], exc)

    def run(self):
        try:
            emit("run", True, to=self.room.room_code)
            stdout, stderr = self.room.run()
            emit("run", False, to=self.room.room_code)

            emit("stdout", stdout, to=self.room.room_code)
            emit("stderr", stderr, to=self.room.room_code)
            
            logger.debug(f"[STDOUT]@[{self.room.room_code}] {repr(self.room.stdout)}")
            logger.debug(f"[STDERR]@[{self.room.room_code}] {repr(self.room.stderr)}")
        
        except Exception as exc:
            self.__sendError__(["Error occured while trying to run the script:"], exc)
            emit("run", False, to=self.room.room_code)