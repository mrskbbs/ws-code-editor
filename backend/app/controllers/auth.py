from flask import Request, Response, make_response
from app.utils import createUserToken


class AuthController():
    request: Request
    
    def __init__(self, request: Request):
        self.request = request
    
    def getUserToken(self) -> Response:
        # Create a token
        if self.request.cookies.get("auth") == None:
            response = make_response()
            response.status = 201

            token = createUserToken(self.request)
            response.set_cookie("auth", token, max_age=None)

            return response

        # User already has a token
        response = make_response()
        response.status = 200

        return response