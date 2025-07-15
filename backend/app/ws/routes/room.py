from flask import request
from flask_socketio import Namespace
import uuid

from app.middleware.auth import authMiddleware
from app.models.room import RoomDynamicModel
from app.ws.controllers.room import RoomWSController


class RoomWSRoutes(Namespace):
    rooms: dict[uuid.UUID, RoomDynamicModel] = dict()

    def __init__(self, namespace = None):
        super().__init__(namespace)

    def on_connect(self):
        authMiddleware(request)
        RoomWSController(request, self.rooms).connect()

    def on_disconnect(self):
        RoomWSController(request, self.rooms).disconnect()

    def on_code(self, data: dict[int, str | None]):
        RoomWSController(request, self.rooms).setCode(data)

    def on_stdin(self, data: dict[int, str | None]):
        RoomWSController(request, self.rooms).setStdin(data)

    def on_code_location(self, data: list[int]):
        RoomWSController(request, self.rooms).locationCode(data)

    def on_stdin_location(self, data: list[int]):
        RoomWSController(request, self.rooms).locationStdin(data)

    def on_run(self):
        RoomWSController(request, self.rooms).run()