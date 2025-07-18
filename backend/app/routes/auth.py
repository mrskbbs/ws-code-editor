from flask import Blueprint, request
from app.controllers.auth import AuthController
from app.middleware.auth import authMiddleware


router = Blueprint("auth", __name__, url_prefix="/auth")


@router.get("/me")
def getMyself():
    authMiddleware(request)
    return AuthController(request).getMyself()

@router.post("/signup")
def signup():
    return AuthController(request).signup()

@router.post("/login")
def login():
    return AuthController(request).login()

@router.post("/logout")
def logout():
    return AuthController(request).logout()