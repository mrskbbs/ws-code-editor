from app.routers import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ORIGIN_REGEX
from app.lifespan import appLifespan
import uvicorn

app = FastAPI(
    root_path="/api/v1",
    lifespan=appLifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_headers = [],
    allow_origin_regex = ORIGIN_REGEX,
    allow_methods = ["GET", "POST", "DELETE", "PUT"],
    allow_credentials = True,
)

app.include_router(auth_router)
app.include_router(rooms_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="localhost")
