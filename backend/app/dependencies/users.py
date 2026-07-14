from fastapi.requests import HTTPConnection
from sqlalchemy import select
from typing import Annotated
from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
import jwt
from app.config import JWT_KEY, JWT_ALGO
from app.db import DbDep
from app.db.models.user import User

async def getUser(conn: HTTPConnection, db: DbDep):
    auth_token = conn.cookies.get("auth_token")
    if not auth_token:
        if isinstance(conn, WebSocket):
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Unauhtorized")
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
        if isinstance(conn, WebSocket):
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Unauhtorized, invalid token")
        raise HTTPException(
           status.HTTP_401_UNAUTHORIZED, 
           { "message": "Unauhtorized, invalid token" }
        )

    user = await db.scalar(
        select(User)
        .where(User.id == payload.get("id"))
    )

    if not user:
        if isinstance(conn, WebSocket):
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Failed to authorize")
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            { "message": "Failed to authorize" },
        )

    return user

UserDep = Annotated[User, Depends(getUser)]
