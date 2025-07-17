import uuid
from flask import Request, make_response
from flask_socketio import emit, join_room, leave_room
from app.models.room import RoomModel
from app.models.user import UserModel
from app.models.room import RoomModelNew
from app.models.user import UserModelNew
from app.services.room import RoomService
from app.utils import injectUser, logger

class RoomController():
    def __init__(self, request: Request):
        self.request = request


    @injectUser
    def __isRoomMember__(self, room_id: uuid.UUID, user: UserModelNew):
        return room_id in set(room.id for room in user.rooms)
    

    @injectUser
    def __isRoomCreator__(self, room_id: uuid.UUID, user: UserModelNew):
        room = RoomService().get(room_id)
        return room.creator_id_fk == user.id

    
    @injectUser
    def getMy(self, user: UserModelNew):
        response = make_response()
        try:
            rooms: list[RoomModelNew] = RoomService().getMy(user)

            response.data = [room.to_dict(
                only=(
                    'id',
                    'name',
                    'users.id',
                    'users.username',
                    'creator.id',
                    'creator.username',
                    'created_at',
                )
            ) for room in rooms]
            response.status = 200

        except Exception as exc:
            logger.error(exc)
            response.status = 500

        finally:
            return response
    

    @injectUser
    def create(self, user: UserModelNew):
        response = make_response()
        try:
            room: RoomModelNew = RoomService().create(self.body, user)
            response.status = 201
            response.data = {"id": str(room.id)}

        except Exception as exc:
            logger.error(exc)
            response.status = 500
        
        finally:
            return response


    @injectUser
    def acceptInvite(self, room_id: str, invite_token: str, user: UserModelNew):
        response = make_response()
        try:
            if self.__isRoomMember__(room_id, user):
                response.status = 400
                return response
            
            RoomService().acceptInvite(room_id, invite_token, user)

            response.status = 200
        
        except ValueError as exc:
            logger.error(exc)
            response.status = 400

        except Exception as exc:
            logger.error(exc)
            response.status = 500

        finally:
            return response


    @injectUser
    def delete(self, room_id: str, user: UserModelNew):
        response = make_response()
        try:
            if not self.__isRoomCreator__(room_id, user):
                response.status = 403
                return response
            
            RoomService().delete(room_id)

            response.status = 200

        except Exception as exc:
            logger.error(exc)
            response.status = 500
        
        finally:
            return response
