from sqlalchemy import select
from typing import Annotated
from fastapi import Depends, HTTPException, Request, WebSocket, status
import jwt
from app.config import JWT_KEY, JWT_ALGO
from app.db import DbDep
from app.db.models.user import User

async def getUser(req: Request, db: DbDep):
    auth_token = req.cookies.get("auth_token")
    if not auth_token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            { "message": "Unauhtorized" }, 
        )

    try:
        payload = jwt.decode(
            auth_token, 
            JWT_KEY, 
            algorithms=[JWT_ALGO],
        )
    except:
        raise HTTPException(
           status.HTTP_401_UNAUTHORIZED, 
           { "message": "Unauhtorized, invalid token" }
        )

    user = await db.scalar(
        select(User)
        .where(User.id == payload.get("id"))
    )

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            { "message": "Failed to authorize" },
        )

    return user

async def getUserWS(ws: WebSocket, db: DbDep):
    auth_token = ws.cookies.get("auth_token")

    if not auth_token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            { "message": "Unauhtorized" }, 
        )

    try:
        payload = jwt.decode(
            auth_token, 
            JWT_KEY, 
            algorithms=[JWT_ALGO],
        )
    except:
        raise HTTPException(
           status.HTTP_401_UNAUTHORIZED, 
           { "message": "Unauhtorized, invalid token" }
        )

    user = await db.scalar(
        select(User)
        .where(User.id == payload.get("id"))
    )

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            { "message": "Failed to authorize" },
        )

    return user

UserDep = Annotated[User, Depends(getUser)]
WSUserDep = Annotated[User, Depends(getUserWS)]
