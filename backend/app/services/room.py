from datetime import datetime
import uuid
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session
from app.config import TIME_FORMAT
from app.db import injectDb
from app.models.room import RoomModelNew
from app.models.user import UserModelNew
from app.types.room import RoomCreate
from app.models.associations import association_user_room
from app.utils import sha256salt, logger

class RoomService():

    @injectDb
    def get(self, room_id: uuid.UUID, db: Session) -> RoomModelNew:
        room = db.get_one(RoomModelNew, room_id)
        return room


    @injectDb
    def getMy(self, user_id: uuid.UUID, db: Session) -> list[RoomModelNew]:
        rooms = (
            db.query(RoomModelNew)
            .join(association_user_room)
            .filter(association_user_room.c.user_id_fk == user_id)
            .all()
        )
        return rooms


    @injectDb
    def create(self, data: RoomCreate, user_id: uuid.UUID, db: Session) -> uuid.UUID:
        try:
            data["creator_id_fk"] = str(user_id)
            data["invite_token"] = sha256salt(f"{datetime.now().strftime(TIME_FORMAT)} {str(user_id)} {data['name']}")
            room = RoomModelNew(**data)
            
            db.add(room)
            db.flush()

            insert(association_user_room).values(user_id_fk=user_id, room_id_fk=room.id)
            if room.id == None: raise Exception("Failed to refresh a room")

            db.commit()
            return room.id
        
        except Exception as exc:
            db.rollback()
            raise exc
    
    
    @injectDb
    def acceptInviteToken(self, room_id: uuid.UUID, invite_token: str, user_id: uuid.UUID, db: Session):
        try:
            room = db.get_one(RoomModelNew, room_id)
    
            if room.invite_token != invite_token:
                raise ValueError("Invalid invitation token")
    
            insert(association_user_room).values(user_id_fk=user_id, room_id_fk=room.id)
            db.commit()

        except Exception as exc:
            db.rollback()
            raise exc


    @injectDb
    def delete(self, room_id: uuid.UUID, db: Session):
        try:
            delete(RoomModelNew).where(id=room_id)
            db.commit()

        except Exception as exc:
            db.rollback()
            raise exc
    