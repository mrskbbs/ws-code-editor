from sqlalchemy.orm import mapped_column
from app.db import Base


class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
