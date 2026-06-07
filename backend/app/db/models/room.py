from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from .room_members import room_members_association_table

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(nullable=False, default="")
    invite_token: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("language.id"), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="owned_rooms")
    members: Mapped[List["User"]] = relationship(secondary=room_members_association_table, back_populates="rooms")
    language: Mapped["Language"] = relationship()
