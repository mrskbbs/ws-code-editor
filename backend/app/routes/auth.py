from flask import Blueprint, request
from app.controllers.auth import AuthController


router = Blueprint("auth", __name__, url_prefix="/auth")

@router.get("/token")
def getUserToken():
    return AuthController(request).getUserToken()