from flask import Request, make_response, session

from app.utils import logger
from app.services.auth import AuthService

def authMiddleware(request: Request):
    response = make_response()
    try:
        user = AuthService().verifyToken(request.cookies.get("auth_token"))
        session["user"] = user
    
    except ValueError as exc:
        logger.error(exc)
        response.status = 400
        return response

    except Exception as exc:
        logger.error(exc)
        response.status = 500
        return response
