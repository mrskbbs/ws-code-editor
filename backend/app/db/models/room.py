from enum import unique
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from .room_members import room_members_association_table

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("language.id"), nullable=False)
    invite_link: Mapped[str] = mapped_column(nullable=False, unique=True)

    owner: Mapped["User"] = relationship(back_populates="owned_rooms")
    members: Mapped[List["User"]] = relationship(secondary=room_members_association_table, back_populates="rooms")
