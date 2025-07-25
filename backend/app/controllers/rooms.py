import json
import uuid
from flask import Request, make_response
from app.db import injectDb
from sqlalchemy.orm import Session
from app.exceptions.base import HTTPBaseException
from app.models.room import RoomModelNew
from app.models.user import UserModelNew
from app.services.room import RoomService
from app.types.auth import AuthSessionInfo
from app.utils import injectUser, logger
from app.exceptions import room as room_exc

class RoomController():
    def __init__(self, request: Request):
        self.request = request
        
        if (request.headers.get("Content-Type") == "application/json"):
            self.body = request.get_json() 

    @injectDb   
    def __isRoomMember__(self, room_id: uuid.UUID, user_id: uuid.UUID, db: Session):
        user = db.get_one(UserModelNew, user_id)
        return str(room_id) in set(str(room.id) for room in user.rooms)
    

    def __isRoomCreator__(self, room_id: uuid.UUID, user_id: uuid.UUID):
        room = RoomService().get(room_id)
        return room.creator_id_fk == user_id

    
    @injectUser
    def getMy(self, user: AuthSessionInfo):
        response = make_response()
        try:
            rooms: list[RoomModelNew] = RoomService().getMy(uuid.UUID(user['id']))

            response.data = json.dumps([room.to_dict(
                only=(
                    'id',
                    'name',
                    'users.id',
                    'users.username',
                    'creator.id',
                    'creator.username',
                    'created_at',
                )
            ) for room in rooms])
            response.status = 200
        
        except HTTPBaseException as exc:
            logger.error(exc)
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })

        except Exception as exc:
            logger.error(exc)
            response.status = 500

        finally:
            return response
    

    @injectUser
    def create(self, user: AuthSessionInfo):
        response = make_response()
        try:
            room_id: uuid.UUID = RoomService().create(self.body, uuid.UUID(user['id']))
            response.status = 201
            response.data = json.dumps({"id": str(room_id)})

        except HTTPBaseException as exc:
            logger.error(exc)
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })

        except Exception as exc:
            logger.error(exc)
            response.status = 500
            response.data = json.dumps({
                "message": "Failed to create a room"
            })
        
        finally:
            return response


    @injectUser
    def acceptInvite(self, room_id: str, invite_token: str, user: AuthSessionInfo):
        response = make_response()
        try:
            if self.__isRoomMember__(room_id, uuid.UUID(user['id'])):
                raise room_exc.AlreadyRoomMember()
            
            RoomService().acceptInvite(room_id, invite_token, uuid.UUID(user['id']))

            response.status = 200
        
        except HTTPBaseException as exc:
            logger.error(exc)
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })

        except Exception as exc:
            logger.error(exc)
            response.status = 500

        finally:
            return response


    @injectUser
    def delete(self, room_id: str, user: AuthSessionInfo):
        response = make_response()
        try:
            if not self.__isRoomCreator__(room_id, uuid.UUID(user['id'])):
                raise room_exc.NotRoomCreator()
            
            RoomService().delete(room_id)

            response.status = 200

        except HTTPBaseException as exc:
            logger.error(exc)
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })

        except Exception as exc:
            logger.error(exc)
            response.status = 500
            response.data = json.dumps({
                "message": "Failed to delete a room"
            })
        
        finally:
            return response
