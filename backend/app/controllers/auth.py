from flask import Request, Response, make_response
from app.services.auth import AuthService
from app.utils import createUserToken, logger

class AuthController():
    request: Request
    
    def __init__(self, request: Request):
        self.request = request
        self.body = request.get_json()
        self.auth_token = request.cookies.get("auth_token")
    

    def __addTokenCookie__(self, response: Response, token: str):
        response.set_cookie("auth_token", token) # TODO: SOME SECURITY IN TOKEN SETTINGS


    def verifyToken(self):
        user = AuthService().verifyToken(self.auth_token)
        return user


    def signup(self):
        response = make_response()
        try: 
            if self.auth_token:
                raise Exception("You need to log out first")
            
            token = AuthService().signup(self.body, self.request.user_agent)
            self.__addTokenCookie__(response, token)
            response.status = 201
        except Exception as exc:
            response.status = 500
        finally:
            return response

    
    def login(self):
        response = make_response()
        try: 
            if self.auth_token:
                raise Exception("You need to log out first")

            token = AuthService().login(self.body, self.request.user_agent)
            self.__addTokenCookie__(response, token)
            response.status = 201
        except Exception as exc:
            response.status = 500
        finally:
            return response


    def logout(self):
        response = make_response()
        try: 
            if not self.auth_token:
                raise KeyError("No authentication token provided")

            AuthService().logout(self.auth_token)
            self.__addTokenCookie__(response, "")
            response.status = 200
        except KeyError as exc:
            response.status = 400
        except Exception as exc:
            response.status = 500
        finally:
            return response