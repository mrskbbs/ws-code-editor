from fastapi import APIRouter, Request, Response

rooms_router = APIRouter()

@rooms_router.get("/")
async def getRooms(req: Request, res: Response):
    pass

@rooms_router.post("/")
async def createRoom(room_data, req: Request, res: Response):
    pass

@rooms_router.get("/{id}")
async def getRoom(id: int, req: Request, res: Response):
    pass

@rooms_router.put("/{id}")
async def editRoom(id: int, req: Request, res: Response):
    pass

@rooms_router.delete("/{id}")
async def deleteRoom(id: int, req: Request, res: Response):
    pass

@rooms_router.websocket("/{id}/ws")
async def roomWS():
    pass

@rooms_router.get("/{id}/invite/{invite_token}")
async def roomInvite(id: int, invite_token: str, req: Request, res: Response):
    pass
