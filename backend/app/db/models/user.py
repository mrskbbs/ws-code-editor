from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from .room_members import room_members_association_table

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    owned_rooms: Mapped[List["Room"]] = relationship(back_populates="owner")
    rooms: Mapped[List["Room"]] = relationship(secondary=room_members_association_table, back_populates="members")

