from fastapi import APIRouter, Depends, HTTPException, Response, status
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError

from app.db import getDb
from app.db.models.user import User
from app.schemas.users import UserCreds
from app.utils import sha256salt
from app.config import JWT_ALGO, JWT_KEY, SALT
from app.dependencies import getUser

auth_router = APIRouter(prefix="/auth")

@auth_router.get("/")
async def getAuth(user: User = Depends(getUser)):
    return {
        "id": user.id,
        "username": user.username,
    }

@auth_router.post("/signup")
async def signup(data: UserCreds, res: Response, db: AsyncSession = Depends(getDb)):
    try:
        user = User(
            username=data.username,
            password=sha256salt(data.password, SALT),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

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

        return user.info()
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

        user = await db.scalar(
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

        return user.info()
    except HTTPException as e: raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "There was an error")

@auth_router.post("/logout", dependencies=[Depends(getUser)])
async def logout(res: Response):
    try:
        res.delete_cookie("auth_token")

        return { "message": "Logged out" }
    except HTTPException as e: raise e
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "There was an error")



