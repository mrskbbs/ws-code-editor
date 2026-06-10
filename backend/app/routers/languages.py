from fastapi import APIRouter
from sqlalchemy import select

from app.db import DbDep
from app.db.models.language import Language 


languages_router = APIRouter(prefix="/languages")

@languages_router.get("/")
async def getLanguages(db: DbDep):
    languages = (await db.execute(select(Language))).scalars().all()

    return languages

