from fastapi import APIRouter, Depends, HTTPException, Request, Response
import jwt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import getDb
from app.db.models.user import User
from app.middleware.auth import AuthMiddleware
from app.utils import sha256salt
from app.config import JWT_ALGO, JWT_KEY, SALT

auth_router = APIRouter(prefix="/auth")

@auth_router.get("/", dependencies=[Depends(AuthMiddleware)])
async def getAuth(req: Request, res: Response):
    return {
        "id": req.state.user.id,
        "username": req.state.user.username,
    }

@auth_router.post("/signup")
async def signup(data, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
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
            500, 
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

    return user._mapping
    

@auth_router.post("/login")
async def login(data, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
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
            401, 
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

    return user._mapping

@auth_router.post("/logout", dependencies=[Depends(AuthMiddleware)])
async def logout(req: Request, res: Response):
    res.delete_cookie("auth_token")

    return { "message": "Logged out" }



