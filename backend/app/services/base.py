from functools import wraps

from fastapi import HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

def handleErrors(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except HTTPException as e: 
            await self.db.rollback()
            raise e
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                { "message": "There was an error" }
            )
    return wrapper

class BaseService():
    def __init__(self, req: Request, res: Response, db: AsyncSession):
        self.req = req
        self.res = res
        self.db = db


