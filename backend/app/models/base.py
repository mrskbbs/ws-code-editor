from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_serializer import SerializerMixin

class Base(DeclarativeBase, SerializerMixin):
    pass