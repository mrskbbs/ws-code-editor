from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from app.db import Base


room_members_association_table = Table(
    "room_members",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True, nullable=False),
    Column("room_id", ForeignKey("rooms.id"), primary_key=True, nullable=False),
)
