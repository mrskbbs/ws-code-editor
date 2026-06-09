from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import jwt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError

from app.db import getDb
from app.db.models.user import User
from app.middleware.auth import authMiddleware
from app.schemas.users import UserCreds
from app.utils import sha256salt
from app.config import JWT_ALGO, JWT_KEY, SALT

auth_router = APIRouter(prefix="/auth")

@auth_router.get("/")
async def getAuth(user: User = Depends(authMiddleware)):
    return {
        "id": user.id,
        "username": user.username,
    }

@auth_router.post("/signup")
async def signup(data: UserCreds, res: Response, db: AsyncSession = Depends(getDb)):
    try:
        user = (await db.execute(
            insert(User)
            .values(
                username=data.username,
                password=sha256salt(data.password, SALT),
            )
            .returning(User.id, User.username)
        )).one_or_none()

        if not user: 
            await db.rollback()
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, 
                { "message": "Sign up failed" },
            )

        await db.commit()

        # TODO: security later 
        auth_token = jwt.encode(
            { "id": user.id },
            JWT_KEY,
            algorithm=JWT_ALGO,
        )

        res.set_cookie(
            "auth_token", 
            auth_token, 
            max_age=None,
            expires=None,
            httponly=True,
            secure=True,
            path="/api/v1",
            samesite="strict",
        )

        return dict(user._mapping)
    except HTTPException as e: raise e
    except UniqueViolationError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid username")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "There was an error")

@auth_router.post("/login")
async def login(data: UserCreds, res: Response, db: AsyncSession = Depends(getDb)):
    try:
        hashed_password = sha256salt(data.password, SALT)

        user = (await db.execute(
            select(User.id, User.username)
            .where(
                User.username == data.username,
                User.password == hashed_password,
            )
        )).one_or_none()

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

        res.set_cookie(
            "auth_token", 
            auth_token,
            max_age=None,
            expires=None,
            httponly=True,
            secure=True,
            path="/api/v1",
            samesite="strict",
        )

        return dict(user._mapping)
    except HTTPException as e: raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "There was an error")

@auth_router.post("/logout", dependencies=[Depends(authMiddleware)])
async def logout(res: Response):
    try:
        res.delete_cookie("auth_token")

        return { "message": "Logged out" }
    except HTTPException as e: raise e
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "There was an error")



