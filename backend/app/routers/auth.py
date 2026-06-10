from typing import Annotated
from fastapi import APIRouter, Depends

from app.schemas.users import UserCreds
from app.dependencies.users import getUser, UserDep
from app.services.auth import *

auth_router = APIRouter(prefix="/auth")

ServiceDep = Annotated[AuthService, Depends(getAuthService)]

@auth_router.get("/", dependencies=[Depends(getUser)])
async def getAuth(service: ServiceDep, user: UserDep):
    return await service.getAuth(user)

@auth_router.post("/signup")
async def signup(service: ServiceDep, data: UserCreds):
    return await service.signup(data)

@auth_router.post("/login")
async def login(service: ServiceDep, data: UserCreds):
    return await service.login(data)

@auth_router.post("/logout", dependencies=[Depends(getUser)])
async def logout(service: ServiceDep):
    return await service.logout()

