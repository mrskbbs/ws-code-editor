from flask import Blueprint, make_response, request
from app.controllers.auth import AuthController
from app.utils import createUserToken


router = Blueprint("auth", __name__, url_prefix="/auth")

@router.get("/token")
def getUserToken():
    return AuthController(request).getUserToken()