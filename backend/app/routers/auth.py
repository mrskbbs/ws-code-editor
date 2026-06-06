from fastapi import APIRouter, Request, Response

auth_router = APIRouter()

@auth_router.get("/")
async def getAuth(req: Request, res: Response):
    pass

@auth_router.post("/signup")
async def signup(req: Request, res: Response):
    pass

@auth_router.post("/login")
async def login(req: Request, res: Response):
    pass

@auth_router.post("/logout")
async def logout(req: Request, res: Response):
    pass



