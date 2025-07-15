from datetime import datetime
import uuid
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session
from app.db import injectDb
from app.models.room import RoomModelNew
from app.models.user import UserModelNew
from app.types.room import RoomCreate
from app.models.associations import association_room_user
from app.utils import sha256salt, logger

class RoomService():

    @injectDb
    def get(self, room_id: uuid.UUID, db: Session) -> RoomModelNew:
        room = db.get_one(RoomModelNew, uuid.UUID(room_id))
        return room


    @injectDb
    def getMy(self, user: UserModelNew, db: Session) -> list[RoomModelNew]:
        return user.rooms


    @injectDb
    def create(self, data: RoomCreate, user: UserModelNew, db: Session) -> uuid.UUID:
        try:
            data["creator_id_fk"] = str(user.id)
            data["invite_token"] = sha256salt(f"{datetime.now().strftime()} {str(user.id)} {data['name']}")
            room = RoomModelNew(**data)
            db.flush()
            insert(association_room_user).values(user_id_fk=user.id, room_id_fk=room.id)
            db.commit()

            return room.id    
        
        except Exception as exc:
            db.rollback()
            raise exc
    
    
    @injectDb
    def acceptInviteToken(self, room_id: uuid.UUID, invite_token: str, user: UserModelNew, db: Session):
        try:
            room = db.get_one(RoomModelNew, room_id)
    
            if room.invite_token != invite_token:
                raise ValueError("Invalid invitation token")
    
            insert(association_room_user).values(user_id_fk=user.id, room_id_fk=room.id)
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
    