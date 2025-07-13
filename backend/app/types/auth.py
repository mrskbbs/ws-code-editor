from typing import TypedDict

class AuthLogin(TypedDict):
    email: str
    password: str

class AuthSignup(TypedDict):
    username: str
    email: str
    password: str
    
class AuthJWTPayload(TypedDict):
    id: str
    iat: int