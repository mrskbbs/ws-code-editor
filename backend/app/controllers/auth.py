from datetime import datetime
import json
from flask import Request, Response, make_response, session
from app.exceptions.base import HTTPBaseException
from app.models.user import UserModelNew
from app.services.auth import AuthService
from app.types.auth import AuthSessionInfo
from app.utils import injectUser, logger
from app.exceptions import auth as auth_exc
class AuthController():
    request: Request
    
    def __init__(self, request: Request):
        self.request = request
        if (request.headers.get("Content-Type") == "application/json"):
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
    def getMyself(self, user: AuthSessionInfo):
        response = make_response()
        
        if user == None:
            exc = auth_exc.InvalidToken()
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })
            return response
        
        response.status = 200
        response.data = json.dumps(user)

        return response


    def signup(self):
        response = make_response()
        try: 
            if self.auth_token:
                raise auth_exc.LogoutRequired()
            
            token = AuthService().signup(self.body, self.request.user_agent.string)
            self.__addTokenCookie__(response, token)
            response.status = 201

        except HTTPBaseException as exc:
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })

        except Exception as exc:
            logger.error(exc)
            response.status = 500

        finally:
            return response

    
    def login(self):
        response = make_response()
        try: 
            if self.auth_token:
                raise auth_exc.LogoutRequired()

            token = AuthService().login(self.body, self.request.user_agent.string)
            self.__addTokenCookie__(response, token)
            response.status = 201
        
        except HTTPBaseException as exc:
            logger.error(exc)
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })
        
        except Exception as exc:
            logger.error(exc)
            response.status = 500
        
        finally:
            return response


    def logout(self):
        response = make_response()
        try: 
            if not self.auth_token:
                raise auth_exc.InvalidToken()

            AuthService().logout(self.auth_token)
            self.__removeTokenCookie__(response)
            session.clear()
            response.status = 200
        
        except HTTPBaseException as exc:
            response.status = exc.status_code
            response.data = json.dumps({
                "message": exc.message
            })
        
        except Exception as exc:
            logger.error(exc)
            response.status = 500
        
        finally:
            return response