from datetime import datetime
import uuid
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, joinedload
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
            .options(joinedload(RoomModelNew.creator), joinedload(RoomModelNew.users))
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

            db.execute(
                insert(association_user_room)
                .values(
                    user_id_fk=user_id, 
                    room_id_fk=room.id
                )
            )
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
    
            db.execute(
                insert(association_user_room)
                .values(
                    user_id_fk=user_id, 
                    room_id_fk=room.id
                )
            )

            db.commit()

        except Exception as exc:
            db.rollback()
            raise exc


    @injectDb
    def delete(self, room_id: uuid.UUID, db: Session):
        try:
            db.execute(
                delete(RoomModelNew).where(id=room_id)
            )
            db.commit()

        except Exception as exc:
            db.rollback()
            raise exc
    

    @injectDb
    def saveState(self, room_id: uuid.UUID, code: list[str], stdin: list[str], db: Session):
        try:
            db.execute(
                update(RoomModelNew).where(
                    RoomModelNew.id==room_id
                ).values(
                    code="\n".join(code),
                    stdin="\n".join(stdin),
                )
            )
            db.commit()
        except Exception as exc: 
            logger.error(exc)
            logger.warning(f"Failed to save state for room #{self.room.id}")
            db.rollback()
            raise exc
        

    @injectDb
    def isAllowedToEnter(self, user_id: uuid.UUID, room_id: uuid.UUID, db: Session) -> bool:
        try:
            db.query(association_user_room).where(
                association_user_room.c.user_id_fk == user_id,
                association_user_room.c.room_id_fk == room_id,
            ).one()
            return True
        except:
            return False