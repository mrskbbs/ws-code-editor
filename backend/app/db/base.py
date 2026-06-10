from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import DB_URL, TESTS_DB_URL

engine = create_async_engine(DB_URL)
test_engine = create_async_engine(TESTS_DB_URL)

Base = declarative_base()

Session = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
)
TestSession = async_sessionmaker(
    test_engine,
    autoflush=False,
    autocommit=False,
)

async def getDb(): 
    session = Session()
    try:
        yield session
    finally:
        await session.close()

async def getTestDb(): 
    session = TestSession()
    try:
        yield session
    finally:
        await session.close()

DbDep = Annotated[AsyncSession, Depends(getDb)]
TestDbDep = Annotated[AsyncSession, Depends(getTestDb)]
