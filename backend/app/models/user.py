from flask import Request

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, func

from app.models.base import Base
from app.models.associations import association_user_room

class UserModelNew(Base):
    __tablename__ = "user_"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        unique=True, 
        server_default=func.gen_random_uuid()
    )
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    sessions: Mapped[list["SessionModel"]] = relationship(back_populates="user")
    rooms: Mapped[list["RoomModelNew"]] = relationship(
        secondary=association_user_room,
        back_populates="user"
    )


class UserModel():
    def __init__(self, request: Request):
        if request.sid == None:
            raise ValueError("SID is NULL")
        
        if request.cookies.get("auth") == None:
            raise ValueError("User token is NULL")
        
        self.sid = request.sid
        self.user_token = request.cookies.get("auth")

    def __str__(self):
        return self.user_token+"@"+self.sid
    
    def __repr__(self):
        return f"TOKEN[{self.user_token}]@SID[{self.sid}]"

    def __eq__(self, other):
        if not isinstance(other, UserModel):
            return False
        
        return self.user_token == other.user_token and self.sid == other.sid

    def __hash__(self):
        return hash(self.user_token + self.sid)