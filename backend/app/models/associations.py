from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import mapped_column, relationship

from app.model.base import Base

association_user_room = Table(
    "association_room_user",
    Base.metadata,
    mapped_column("user_id_fk", ForeignKey("user_.id"), primary_key=True, ondelete="CASCADE", onupdate="CASCADE"),
    mapped_column("room_id_fk", ForeignKey("room.id"), primary_key=True, ondelete="CASCADE", onupdate="CASCADE")
)
