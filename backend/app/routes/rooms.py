from venv import logger
from flask import request
from flask_socketio import Namespace, emit
from app.controllers.rooms import RoomController
from app.middleware.auth import authMiddleware
from app.models.room import RoomModel


from flask import Blueprint, request
from app.controllers.auth import AuthController

router = Blueprint("rooms", __name__, url_prefix="/rooms")

@router.before_request
def middleware():
    logger.debug("BEFORE REQ")
    authMiddleware(request)

@router.post("/")
def createRoom():
    return RoomController(request).create()

@router.get("/")
def getMyRooms():
    return RoomController(request).getMy()

@router.delete("/<room_id>")
def deleteRoom(room_id: str):
    return RoomController(request).delete(room_id)

@router.get("/<room_id>/invite/<invite_token>")
def acceptInvite(room_id: str, invite_token: str):
    return RoomController(request).acceptInvite(room_id, invite_token)