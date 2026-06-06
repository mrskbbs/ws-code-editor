from app.routers import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import origin_regex
from app.middleware.auth import AuthMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_headers = [],
    allow_origin_regex = origin_regex,
    allow_methods = ["GET", "POST", "DELETE", "PUT"],
    allow_credentials = True,
)

app.add_middleware(
    AuthMiddleware,
)

app.include_router(auth_router)
app.include_router(rooms_router)
