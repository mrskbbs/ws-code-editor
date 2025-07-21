import datetime
import jwt
import uuid
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from app.config import JWT_KEY, JWT_ALGO
from app.db import injectDb
from app.models.session import SessionModel
from app.models.user import UserModelNew
from app.types.auth import *
from app.utils import sha256salt, unwrapForWhereClasue


class AuthService():
    def __createToken__(self, id: uuid.UUID) -> str:
        token = jwt.encode({
            "id": str(id),
            "iat": int(datetime.datetime.now().timestamp())
        }, JWT_KEY, JWT_ALGO)
        return token
    

    @injectDb
    def verifyToken(self, auth_token: str | None, db: Session) -> UserModelNew:
        if not auth_token: raise ValueError("Invalid authentication token")

        payload: AuthJWTPayload = jwt.decode(auth_token, JWT_KEY, [JWT_ALGO], reqiure=["iat"])

        if not payload["id"]: raise ValueError("Invalid authentication token")

        user = db.get_one(UserModelNew, payload["id"])
        return user
    

    @injectDb
    def signup(self, body: AuthSignup, user_agent: str | None, db: Session):
        try:
            body["password"] = sha256salt(body["password"])
            user = UserModelNew(**body)
            
            db.add(user)
            db.flush()

            auth_token = self.__createToken__(user.id)
            
            session = SessionModel(
                user_id_fk = user.id,
                auth_token = auth_token,
                user_agent = user_agent,
            )
            db.add(session)
            db.commit()

            return auth_token

        except Exception as exc:
            db.rollback()
            raise exc


    @injectDb
    def login(self, body: AuthLogin, user_agent: str, db: Session):
        try:
            body["password"] = sha256salt(body["password"])

            user = db.scalars(
                select(UserModelNew).where(and_(
                    UserModelNew.email == body["email"],
                    UserModelNew.password == body["password"],
                ))
            ).first()
            
            if not user: raise Exception("Invalid credentials")

            auth_token = self.__createToken__(user.id)
            session = SessionModel(
                user_id_fk = user.id,
                auth_token = auth_token,
                user_agent = user_agent,
            )
            db.add(session)
            db.commit()

            return auth_token

        except Exception as exc:
            db.rollback()
            raise exc


    @injectDb
    def logout(self, auth_token: str, db: Session):
        try:
            payload: AuthJWTPayload = jwt.decode(auth_token, JWT_KEY, [JWT_ALGO]) 
            payload["id"] = uuid.UUID(payload["id"])

            delete(SessionModel).where(
                and_(
                    SessionModel.auth_token == auth_token,
                    SessionModel.user_id_fk == payload["id"],
                )
            )
            
            db.commit()

        except Exception as exc:
            db.rollback()
            raise exc