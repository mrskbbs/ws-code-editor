from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from .room_members import room_members

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)

    owned_rooms: Mapped[List["Room"]] = relationship(back_populates="owner")
    rooms: Mapped[List["Room"]] = relationship(secondary=room_members, back_populates="members")

    def info(self):
        return {
            "id": self.id,
            "username": self.username,
        }

