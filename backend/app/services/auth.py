from fastapi import Depends, HTTPException, Request, Response, status
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import JWT_ALGO, JWT_KEY, SALT
from app.db import DbDep
from app.db.models.user import User
from app.services.base import *
from app.schemas.users import UserCreds
from app.utils import sha256salt


async def getAuthService(req: Request, res: Response, db: DbDep): 
    return AuthService(req, res, db)

class AuthService(BaseService):

    @handleErrors
    async def getAuth(self, user: User):
        return {
            "id": user.id,
            "username": user.username,
        }

    @handleErrors
    async def signup(self, data: UserCreds):
        user = User(
            username=data.username,
            password=sha256salt(data.password, SALT),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # TODO: security later 
        auth_token = jwt.encode(
            { "id": user.id },
            JWT_KEY,
            algorithm=JWT_ALGO,
        )

        self.res.set_cookie(
            "auth_token", 
            auth_token, 
            max_age=None,
            expires=None,
            httponly=True,
            secure=True,
            path="/api/v1",
            samesite="strict",
        )

        return user.info()

    
    @handleErrors
    async def login(self, data: UserCreds):
        hashed_password = sha256salt(data.password, SALT)

        user = await self.db.scalar(
            select(User)
            .where(
                User.username == data.username,
                User.password == hashed_password,
            )
        )

        if not user: 
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, 
                { "message": "Failed to log in" },
            )

        # TODO: security later 
        auth_token = jwt.encode(
            { "id": user.id },
            JWT_KEY,
            algorithm=JWT_ALGO,
        )

        self.res.set_cookie(
            "auth_token", 
            auth_token,
            max_age=None,
            expires=None,
            httponly=True,
            secure=True,
            path="/api/v1",
            samesite="strict",
        )

        return user.info()

    @handleErrors
    async def logout(self):
        self.res.delete_cookie("auth_token")
        return { "message": "Logged out" }

