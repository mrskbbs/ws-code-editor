from datetime import datetime
from flask import Request, Response, make_response
from app.models.user import UserModelNew
from app.services.auth import AuthService
from app.utils import createUserToken, injectUser, logger

class AuthController():
    request: Request
    
    def __init__(self, request: Request):
        self.request = request
        self.body = request.get_json()
        self.auth_token = request.cookies.get("auth_token")
    

    def __addTokenCookie__(self, response: Response, token: str):
        response.set_cookie("auth_token", token, max_age=int(2.592e6)) # Available for one month


    def __removeTokenCookie__(self, response: Response):
        response.set_cookie("auth_token", "", max_age=0)


    def verifyToken(self):
        user = AuthService().verifyToken(self.auth_token)
        return user


    @injectUser
    def getMyself(self, user: UserModelNew):
        response = make_response()
        
        if user == None:
            response.status = 403
            return response

        response.data = user.to_dict(only=("id","username",))
        response.status = 200

        return response


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
            self.__removeTokenCookie__(response)
            response.status = 200
        except KeyError as exc:
            response.status = 400
        except Exception as exc:
            response.status = 500
        finally:
            return response