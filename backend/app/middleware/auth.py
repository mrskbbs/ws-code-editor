from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Depends, HTTPException, Request, Response
import jwt
from app.config import JWT_KEY, JWT_ALGO
from app.db import getDb
from app.db.models.user import User

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint, db: AsyncSession = Depends(getDb)) -> Response:
        auth_token = request.cookies.get("auth_token")
        if not auth_token:
            raise HTTPException(
                401, 
                { "message": "Unauhtorized" }, 
            )

        payload = jwt.decode(
            auth_token, 
            JWT_KEY, 
            algorithms=[JWT_ALGO],
        )

        user = await db.scalar(
            select(User)
            .where(User.id == payload.get("id"))
        )

        if not user:
            raise HTTPException(
                401,
                { "message": "Failed to authorize" },
            )

        request.state.user = user

        res = await call_next(request)

        return res
